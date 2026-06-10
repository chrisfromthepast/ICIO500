import pcbnew
import sys
import os

pcb_path = os.path.join("build", "icio500", "icio500.kicad_pcb")
board = pcbnew.LoadBoard(pcb_path)

# Board bounds:
# X: 50.65 to 203.0 (safely say 52.0 to 193.0 for components to avoid edge)
# Y: 55.0 to 160.0 (safely say 57.0 to 158.0)

SAFE_MIN_X = 52.0
SAFE_MAX_X = 193.0
SAFE_MIN_Y = 57.0
SAFE_MAX_Y = 158.0

errors = []
for fp in board.GetFootprints():
    ref = fp.GetReference()
    box = fp.GetBoundingBox()
    left = box.GetLeft() / 1e6
    right = box.GetRight() / 1e6
    top = box.GetTop() / 1e6
    bottom = box.GetBottom() / 1e6
    
    if left < SAFE_MIN_X or right > SAFE_MAX_X or top < SAFE_MIN_Y or bottom > SAFE_MAX_Y:
        errors.append(f"Footprint {ref} is out of bounds! Limits: ({left:.1f}, {top:.1f}) to ({right:.1f}, {bottom:.1f})")

if errors:
    print("VIOLATIONS FOUND:")
    for e in errors:
        print(e)
    sys.exit(1)
else:
    print("All components are safely within the board bounds.")
    sys.exit(0)
