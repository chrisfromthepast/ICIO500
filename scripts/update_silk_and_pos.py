import pcbnew
import os
import sys

pcb_path = os.path.join("build", "icio500", "icio500.kicad_pcb")
board = pcbnew.LoadBoard(pcb_path)

def mm(v): return int(v * 1_000_000)

# Move U6 and U7 closer to Daisy
DAISY_X, DAISY_Y = 100.0, 130.0
for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref == 'U6':
        fp.SetPosition(pcbnew.VECTOR2I(mm(DAISY_X - 15), mm(DAISY_Y + 15)))  # wait, currently they are at X-15. Let's make it X-8.
        fp.SetPosition(pcbnew.VECTOR2I(mm(DAISY_X - 8), mm(DAISY_Y + 15)))
    elif ref == 'U7':
        fp.SetPosition(pcbnew.VECTOR2I(mm(DAISY_X - 8), mm(DAISY_Y + 30)))

# Move User.Drawings to F.SilkS and make them thicker
for d in board.GetDrawings():
    if isinstance(d, pcbnew.PCB_SHAPE) and d.GetLayerName() == 'User.Drawings':
        d.SetLayer(pcbnew.F_SilkS)
        d.SetWidth(mm(0.2)) # make the bounding box clear
        
pcbnew.SaveBoard(pcb_path, board)
print("Updated positions and moved boxes to SilkS.")
sys.exit(0)
