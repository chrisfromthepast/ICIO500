import pcbnew
import re

PCB_PATH = 'build/icio500/icio500.kicad_pcb'
NETLIST_PATH = 'build/default.net'

b = pcbnew.LoadBoard(PCB_PATH)

# 1. Remove exactly the bad duplicates
to_remove = []
for fp in b.GetFootprints():
    ref = fp.GetReference()
    x = fp.GetPosition().x / 1e6
    if ref == 'U1' and x > 150: # The bad U1 was at 154.3
        to_remove.append(fp)
    elif ref == 'C5' and x > 120: # The bad C5 was at 150.1
        to_remove.append(fp)
    elif ref == 'C6' and x > 120: # The bad C6 was at 150.1
        to_remove.append(fp)

# Remove any orphans not in netlist
with open(NETLIST_PATH, 'r', encoding='utf-8') as f:
    content = f.read()
valid_refs = set(re.findall(r'\(comp\s+\(ref\s+"([^"]+)"', content))
for fp in b.GetFootprints():
    if fp.GetReference() not in valid_refs and fp not in to_remove:
        to_remove.append(fp)

for fp in to_remove:
    b.Remove(fp)

# 2. Strip old board-level F.Silkscreen boxes and text
drawings_to_remove = []
for d in b.GetDrawings():
    layer = b.GetLayerName(d.GetLayer())
    if layer == 'F.Silkscreen':
        drawings_to_remove.append(d)
for d in drawings_to_remove:
    b.Remove(d)

# 3. Rigid body translation using IC as the anchor point
groups = {
    'LINE DRIVER': ('U4', ['U4', 'C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26', 'R7', 'R8'], 145.0, 70.0),
    'SCALING': ('U3', ['U3', 'C15', 'C16', 'C17', 'C18', 'R3', 'R4', 'R5', 'R6'], 100.0, 70.0),
    'BALANCED INPUT': ('U2', ['U2', 'C7', 'C8', 'C13', 'C14', 'R1', 'R2', 'D3', 'D4', 'D5', 'D6'], 160.0, 100.0),
    'POWER': ('U1', ['U1', 'C1', 'C2', 'C3', 'C4', 'C9', 'C10', 'C11', 'C12'], 145.0, 130.0),
    'DIGITAL PROCESSING': ('U5', ['U5', 'U6', 'U7', 'C5', 'C6'], 70.0, 120.0)
}

for name, (ic_ref, refs, target_x, target_y) in groups.items():
    ic_fp = b.FindFootprintByReference(ic_ref)
    if not ic_fp: continue
    
    current_x = ic_fp.GetPosition().x / 1e6
    current_y = ic_fp.GetPosition().y / 1e6
    
    dx = target_x - current_x
    dy = target_y - current_y
    
    for ref in refs:
        fp = b.FindFootprintByReference(ref)
        if fp:
            pos = fp.GetPosition()
            fp.SetPosition(pcbnew.VECTOR2I(int((pos.x/1e6 + dx)*1e6), int((pos.y/1e6 + dy)*1e6)))

# D1 and D2 clear of J1
d1 = b.FindFootprintByReference('D1')
if d1: d1.SetPosition(pcbnew.VECTOR2I(int(180*1e6), int(140*1e6)))
d2 = b.FindFootprintByReference('D2')
if d2: d2.SetPosition(pcbnew.VECTOR2I(int(180*1e6), int(150*1e6)))

# 4. Draw New F.Silkscreen Boxes
new_boxes = {
    'LINE DRIVER': (133, 161, 62, 78),
    'BALANCED INPUT': (141, 176, 91, 107),
    'POWER': (131, 172, 114, 146),
    'SCALING': (88, 116, 63, 76),
    'DIGITAL PROCESSING': (65, 119, 101, 147)
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
    b.Add(create_text(title, minx + 2, miny + 2))

# 5. Clear Tracks and Zones
for t in list(b.Tracks()): b.Remove(t)
for z in list(b.Zones()): b.Remove(z)

b.BuildConnectivity()
pcbnew.SaveBoard(PCB_PATH, b)
print("Rigid translation applied perfectly.")
