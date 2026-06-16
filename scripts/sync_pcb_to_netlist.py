"""
Sync PCB to the ato-generated netlist:
  - Remove any footprint whose designator does NOT appear in the netlist
  - Leave all existing footprint positions and orientations untouched
"""

import pcbnew
import re

NETLIST_PATH = 'build/default.net'
PCB_PATH = 'build/icio500/icio500.kicad_pcb'

# 1. Parse the KiCad S-expression netlist to find all valid designators
# Format: (comp (ref "U1") ...)
with open(NETLIST_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

valid_refs = set(re.findall(r'\(comp\s+\(ref\s+"([^"]+)"', content))

print(f"Netlist has {len(valid_refs)} unique components:")
for r in sorted(valid_refs):
    print(f"  {r}")

# 2. Load the board
board = pcbnew.LoadBoard(PCB_PATH)

# 3. Find footprints NOT in the netlist
to_remove = []
all_refs_on_pcb = {}
for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref not in all_refs_on_pcb:
        all_refs_on_pcb[ref] = []
    all_refs_on_pcb[ref].append(fp)

# Find designators not in netlist (ghosts)
for ref, fps in all_refs_on_pcb.items():
    if ref not in valid_refs:
        for fp in fps:
            pos = fp.GetPosition()
            print(f"ORPHAN (removing): {ref}  X={pos.x/1e6:.2f}  Y={pos.y/1e6:.2f}  val={fp.GetValue()}")
            to_remove.append(fp)

# Find duplicate refs (same ref appears multiple times on PCB)
for ref, fps in all_refs_on_pcb.items():
    if len(fps) > 1 and ref in valid_refs:
        # Keep the one with a real value (not "?") or the first one
        # Remove the others
        fps_sorted = sorted(fps, key=lambda f: (f.GetValue() == '?' or f.GetValue() == 'DC-DC ISO', f.GetPosition().x))
        keep = fps_sorted[0]
        for fp in fps_sorted[1:]:
            pos = fp.GetPosition()
            print(f"DUPLICATE (removing): {ref}  X={pos.x/1e6:.2f}  Y={pos.y/1e6:.2f}  val={fp.GetValue()}")
            to_remove.append(fp)

# 4. Remove them
print(f"\nRemoving {len(to_remove)} footprints...")
for fp in to_remove:
    board.Remove(fp)

board.BuildConnectivity()
pcbnew.SaveBoard(PCB_PATH, board)
print(f"Done. Board saved to {PCB_PATH}")
