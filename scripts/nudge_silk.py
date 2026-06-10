import pcbnew
import os
import sys

pcb_path = os.path.join("build", "icio500", "icio500.kicad_pcb")
board = pcbnew.LoadBoard(pcb_path)

def mm(v): return int(v * 1_000_000)

labels = {
    "OUTPUT STAGE": (164.75, 58.0), # Moved up away from box line
    "LEVEL SCALING": (166.95, 78.5), # Moved up away from line
    "INPUT STAGE": (159.85, 99.5), # Moved up
    "ANALOG PSU": (138.65, 118.5), # Moved up
    "ISOLATED POWER": (125.25, 59.5), # Moved up
    "DAISY DIGITAL": (100.0, 99.5) # Moved up away from pads
}

# Update block labels
for d in board.GetDrawings():
    if isinstance(d, pcbnew.PCB_TEXT):
        txt = d.GetText()
        if txt in labels:
            x, y = labels[txt]
            d.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))

# Update IC values (they are FP_TEXT)
ic_positions = {
    'U1': (125.25, 87.5),  # Lower
    'U2': (178.0, 110.0),  # Further right
    'U3': (178.0, 90.0),   
    'U4': (178.0, 70.0),   
    'U5': (100.0, 161.0),  # Further down
}

for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref in ic_positions:
        val = fp.Value()
        x, y = ic_positions[ref]
        val.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))

pcbnew.SaveBoard(pcb_path, board)
print("Screenprints nudged.")
sys.exit(0)
