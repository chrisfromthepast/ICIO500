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
        # Sort by value ('DC-DC') to ensure we keep the correct footprint for U1
        fps_sorted = sorted(fps, key=lambda f: ('DC-DC' in f.GetValue(), f.GetPosition().x))
        for fp in fps_sorted[1:]:
            to_remove.append(fp)

for fp in to_remove:
    b.Remove(fp)

# 2. Strict Placement Algorithm
placements = {
    'U5': (94, 115), 'U6': (80, 140), 'U7': (105, 140), 'C5': (70, 115), 'C6': (118, 115),
    'U1': (145, 102),
    'U4': (160, 70),
    'U2': (180, 105),
    'U3': (170, 142),
    'D1': (190, 135), 'D2': (190, 145)
}

# Auto-tile surrounding passives
def tile_around(center_x, center_y, refs, spacing=4, max_cols=3):
    start_x = center_x - ((max_cols-1)*spacing/2)
    for i, ref in enumerate(refs):
        col = i % max_cols
        row = i // max_cols
        x = start_x + (col * spacing)
        y = center_y - 8 - (row * spacing) # Place above the IC
        placements[ref] = (x, y)

# POWER passives
tile_around(145, 102, ['C1', 'C2', 'C3', 'C4', 'C9', 'C10', 'C11', 'C12'], max_cols=4)

# LINE DRIVER passives
tile_around(160, 70, ['R7', 'R8', 'C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26'], max_cols=5)

# BALANCED INPUT passives
tile_around(180, 105, ['R1', 'R2', 'C7', 'C8', 'C13', 'C14', 'D3', 'D4', 'D5', 'D6'], max_cols=5)

# SCALING passives
tile_around(170, 142, ['R3', 'R4', 'R5', 'R6', 'C15', 'C16', 'C17', 'C18'], max_cols=4)

for fp in b.GetFootprints():
    ref = fp.GetReference()
    if ref in placements:
        x, y = placements[ref]
        fp.SetPosition(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)))

# 3. Clear Tracks and Zones
for t in list(b.Tracks()):
    b.Remove(t)
for z in list(b.Zones()):
    b.Remove(z)

b.BuildConnectivity()
pcbnew.SaveBoard(PCB_PATH, b)
print("Board arranged professionally.")
