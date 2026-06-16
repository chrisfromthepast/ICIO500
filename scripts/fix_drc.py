import pcbnew
import re
from collections import defaultdict

NETLIST_PATH = 'build/default.net'
PCB_PATH = 'build/icio500/icio500.kicad_pcb'

b = pcbnew.LoadBoard(PCB_PATH)

# 1. Remove duplicates
with open(NETLIST_PATH, 'r', encoding='utf-8') as f:
    content = f.read()
valid_refs = set(re.findall(r'\(comp\s+\(ref\s+"([^"]+)"', content))

ref_map = defaultdict(list)
for fp in b.GetFootprints():
    ref_map[fp.GetReference()].append(fp)

to_remove = []
for ref, fps in ref_map.items():
    if ref not in valid_refs:
        to_remove.extend(fps)
    elif len(fps) > 1:
        fps_sorted = sorted(fps, key=lambda f: ('DC-DC' in f.GetValue(), f.GetPosition().x))
        for fp in fps_sorted[1:]:
            to_remove.append(fp)

for fp in to_remove:
    b.Remove(fp)

# 2. Strip old board-level F.Silkscreen boxes and text to redraw them perfectly
drawings_to_remove = []
for d in b.GetDrawings():
    layer = b.GetLayerName(d.GetLayer())
    if layer == 'F.Silkscreen':
        drawings_to_remove.append(d)
for d in drawings_to_remove:
    b.Remove(d)

# 3. Rigid body translation for organized clusters
groups = {
    'LINE DRIVER': (['U4', 'C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26', 'R7', 'R8'], 149.5, 70.0),
    'SCALING': (['U3', 'C15', 'C16', 'C17', 'C18', 'R3', 'R4', 'R5', 'R6'], 105.0, 75.0),
    'BALANCED INPUT': (['U2', 'C7', 'C8', 'C13', 'C14', 'R1', 'R2', 'D3', 'D4', 'D5', 'D6'], 158.0, 105.0),
    'POWER': (['U1', 'C1', 'C2', 'C3', 'C4', 'C9', 'C10', 'C11', 'C12'], 120.0, 112.5)
}

for name, (refs, target_cx, target_cy) in groups.items():
    min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
    fps = []
    for ref in refs:
        fp = b.FindFootprintByReference(ref)
        if fp:
            fps.append(fp)
            bb = fp.GetBoundingBox()
            min_x = min(min_x, bb.GetLeft() / 1e6)
            max_x = max(max_x, bb.GetRight() / 1e6)
            min_y = min(min_y, bb.GetTop() / 1e6)
            max_y = max(max_y, bb.GetBottom() / 1e6)
            
    if not fps: continue
    
    current_cx = (min_x + max_x) / 2
    current_cy = (min_y + max_y) / 2
    
    dx = target_cx - current_cx
    dy = target_cy - current_cy
    
    for fp in fps:
        pos = fp.GetPosition()
        fp.SetPosition(pcbnew.VECTOR2I(int((pos.x/1e6 + dx)*1e6), int((pos.y/1e6 + dy)*1e6)))

# 4. Handle DIGITAL PROCESSING and loose parts
def set_pos(ref, x, y):
    fp = b.FindFootprintByReference(ref)
    if fp: fp.SetPosition(pcbnew.VECTOR2I(int(x*1e6), int(y*1e6)))

# U5 centered in bottom left (origin placed appropriately to center body near X=80)
set_pos('U5', 55, 145) 
set_pos('U6', 120, 140)
set_pos('U7', 120, 150)
set_pos('C5', 130, 140)
set_pos('C6', 130, 150)

# Edge connector diodes
set_pos('D1', 170, 140)
set_pos('D2', 170, 150)

# 5. Draw New F.Silkscreen Boxes
new_boxes = {
    'LINE DRIVER': (125, 174, 55, 85),
    'BALANCED INPUT': (142, 174, 85, 125),
    'POWER': (100, 140, 95, 130),
    'SCALING': (90, 120, 60, 90),
    'DIGITAL PROCESSING': (51, 140, 131, 160)
}

def create_shape(x1, y1, x2, y2, layer='F.Silkscreen'):
    shape = pcbnew.PCB_SHAPE(b)
    shape.SetShape(pcbnew.SHAPE_T_RECT)
    shape.SetFilled(False)
    shape.SetStart(pcbnew.VECTOR2I(int(x1*1e6), int(y1*1e6)))
    shape.SetEnd(pcbnew.VECTOR2I(int(x2*1e6), int(y2*1e6)))
    shape.SetLayer(b.GetLayerID(layer))
    shape.SetWidth(int(0.2*1e6))
    return shape

def create_text(text_str, x, y, layer='F.Silkscreen'):
    t = pcbnew.PCB_TEXT(b)
    t.SetText(text_str)
    t.SetPosition(pcbnew.VECTOR2I(int(x*1e6), int(y*1e6)))
    t.SetLayer(b.GetLayerID(layer))
    t.SetTextSize(pcbnew.VECTOR2I(int(1.5*1e6), int(1.5*1e6)))
    t.SetTextThickness(int(0.3*1e6))
    return t

for title, (minx, maxx, miny, maxy) in new_boxes.items():
    b.Add(create_shape(minx, miny, maxx, maxy))
    # Place text in top left corner of the box
    b.Add(create_text(title, minx + 2, miny + 2))

# 6. Clear Tracks and Zones
for t in list(b.Tracks()): b.Remove(t)
for z in list(b.Zones()): b.Remove(z)

b.BuildConnectivity()
pcbnew.SaveBoard(PCB_PATH, b)
print("DRC Fix applied.")
