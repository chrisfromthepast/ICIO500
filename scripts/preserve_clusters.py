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

# 2. Rigid body translation for organized clusters
groups = {
    'LINE DRIVER': (['U4', 'C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26', 'R7', 'R8'], 160.0, 70.0),
    'SCALING': (['U3', 'C15', 'C16', 'C17', 'C18', 'R3', 'R4', 'R5', 'R6'], 170.0, 140.5),
    'BALANCED INPUT': (['U2', 'C7', 'C8', 'C13', 'C14', 'R1', 'R2', 'D3', 'D4', 'D5', 'D6'], 180.5, 105.0),
    'POWER': (['U1', 'C1', 'C2', 'C3', 'C4', 'C9', 'C10', 'C11', 'C12'], 145.0, 100.0)
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

# 3. Handle DIGITAL PROCESSING properly
def set_pos(ref, x, y):
    fp = b.FindFootprintByReference(ref)
    if fp: fp.SetPosition(pcbnew.VECTOR2I(int(x*1e6), int(y*1e6)))

# U5 centered in its box
set_pos('U5', 64, 115) 
set_pos('U6', 80, 140)
set_pos('U7', 105, 140)
set_pos('C5', 80, 130)
set_pos('C6', 105, 130)

set_pos('D1', 190, 135)
set_pos('D2', 190, 145)

# 4. Clear Tracks and Zones
for t in list(b.Tracks()): b.Remove(t)
for z in list(b.Zones()): b.Remove(z)

b.BuildConnectivity()
pcbnew.SaveBoard(PCB_PATH, b)
print("Clusters preserved and translated.")
