"""
Clean one-pass script:
1. Remove duplicate footprints not in netlist
2. Move Scaling block between Input and Output
3. Clear all tracks and vias
Does NOT touch Edge.Cuts or any board outline shapes.
"""
import pcbnew
import re

NETLIST_PATH = 'build/default.net'
PCB_PATH = 'build/icio500/icio500.kicad_pcb'

board = pcbnew.LoadBoard(PCB_PATH)

# ── 1. Get valid refs from netlist ──────────────────────────────────────────
with open(NETLIST_PATH, 'r', encoding='utf-8') as f:
    content = f.read()
valid_refs = set(re.findall(r'\(comp\s+\(ref\s+"([^"]+)"', content))
print(f"Netlist: {len(valid_refs)} components")

# ── 2. Remove orphans and duplicates ────────────────────────────────────────
from collections import defaultdict
ref_map = defaultdict(list)
for fp in board.GetFootprints():
    ref_map[fp.GetReference()].append(fp)

to_remove = []
for ref, fps in ref_map.items():
    if ref not in valid_refs:
        to_remove.extend(fps)
        print(f"  ORPHAN: {ref}")
    elif len(fps) > 1:
        # keep the one that is NOT the old DC-DC ISO / not at far-out position
        fps_sorted = sorted(fps, key=lambda f: (
            'DC-DC' in f.GetValue() or f.GetValue() == 'DC-DC ISO',
            f.GetPosition().x
        ))
        for fp in fps_sorted[1:]:
            pos = fp.GetPosition()
            print(f"  DUPLICATE removed: {ref} X={pos.x/1e6:.1f} Y={pos.y/1e6:.1f}")
            to_remove.append(fp)

for fp in to_remove:
    board.Remove(fp)

# ── 3. Move Scaling block between U4 (Y=70) and U2 (Y=105) ─────────────────
SCALING_REFS = {'U3', 'C15', 'C16', 'C17', 'C18', 'R3', 'R4', 'R5', 'R6'}
scale_fps = [fp for fp in board.GetFootprints() if fp.GetReference() in SCALING_REFS]

xs = [fp.GetPosition().x for fp in scale_fps]
ys = [fp.GetPosition().y for fp in scale_fps]
cur_cx = (min(xs) + max(xs)) // 2
cur_cy = (min(ys) + max(ys)) // 2

# Target: X=155mm, Y=87mm (between U4 at Y=70 and U2 at Y=105)
target_cx = int(155 * 1e6)
target_cy = int(87 * 1e6)
dx = target_cx - cur_cx
dy = target_cy - cur_cy

print(f"\nScaling block: moving dX={dx/1e6:.1f}mm dY={dy/1e6:.1f}mm")
for fp in scale_fps:
    pos = fp.GetPosition()
    fp.SetPosition(pcbnew.VECTOR2I(pos.x + dx, pos.y + dy))

# ── 4. Clear all tracks and vias ────────────────────────────────────────────
track_count = 0
for t in list(board.Tracks()):
    board.Remove(t)
    track_count += 1
print(f"Cleared {track_count} tracks/vias")

zone_count = 0
for z in list(board.Zones()):
    board.Remove(z)
    zone_count += 1
print(f"Cleared {zone_count} zones")

# ── 5. Save ──────────────────────────────────────────────────────────────────
board.BuildConnectivity()
pcbnew.SaveBoard(PCB_PATH, board)

# Verify
b2 = pcbnew.LoadBoard(PCB_PATH)
print(f"\n=== Final state ===")
print(f"Tracks: {len(list(b2.Tracks()))}")
print(f"Zones:  {len(list(b2.Zones()))}")
print(f"Comps:  {len(list(b2.GetFootprints()))}")
u3 = b2.FindFootprintByReference('U3')
u2 = b2.FindFootprintByReference('U2')
u4 = b2.FindFootprintByReference('U4')
print(f"U4 (Line Driver)  Y={u4.GetPosition().y/1e6:.1f}")
print(f"U3 (Scaling)      Y={u3.GetPosition().y/1e6:.1f}  <-- between them")
print(f"U2 (Bal. Input)   Y={u2.GetPosition().y/1e6:.1f}")
print("DONE")
