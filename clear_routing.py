import pcbnew
import os
import sys

pcb_path = os.path.join("build", "icio500", "icio500.kicad_pcb")
board = pcbnew.LoadBoard(pcb_path)

print("Removing all tracks and vias...")
tracks = list(board.Tracks())
for t in tracks:
    board.Remove(t)

print("Removing all zones...")
zones = list(board.Zones())
for z in zones:
    board.Remove(z)

print("Saving board...")
pcbnew.SaveBoard(pcb_path, board)
print("Done saving clean board.")
sys.exit(0)
