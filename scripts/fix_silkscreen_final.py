import pcbnew
import os

pcb_path = os.path.join("build", "icio500", "icio500.kicad_pcb")
board = pcbnew.LoadBoard(pcb_path)

def mm(v): return int(v * 1e6)

# 1. Center Section Labels in their boxes
for d in board.GetDrawings():
    if isinstance(d, pcbnew.PCB_TEXT) and d.GetLayer() == pcbnew.F_SilkS:
        text = d.GetText()
        if text == "OUTPUT STAGE": d.SetPosition(pcbnew.VECTOR2I(mm(162.75), mm(64.4)))
        if text == "INPUT STAGE": d.SetPosition(pcbnew.VECTOR2I(mm(157.1), mm(95.7)))
        if text == "LEVEL SCALING": d.SetPosition(pcbnew.VECTOR2I(mm(165.0), mm(127.4)))
        if text == "ANALOG PSU": d.SetPosition(pcbnew.VECTOR2I(mm(135.65), mm(111.5)))
        if text == "ISOLATED POWER": d.SetPosition(pcbnew.VECTOR2I(mm(117.25), mm(99.8)))
        if text == "DAISY DIGITAL": d.SetPosition(pcbnew.VECTOR2I(mm(94.35), mm(95.5)))

# 2. Fix IC Values (Move them to safe empty spots instead of blindly down)
ic_positions = {
    'U1': (117.25, 103.0), # Inside the box, above the component
    'U2': (171.0, 105.0),  # Right of U2
    'U3': (171.0, 138.0),  # Right of U3
    'U4': (171.0, 75.0),   # Right of U4
    'U5': (94.35, 153.0),  # Centered below Daisy Seed
}

for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref in ic_positions:
        val = fp.Value()
        val.SetVisible(True)
        pos = ic_positions[ref]
        val.SetPosition(pcbnew.VECTOR2I(mm(pos[0]), mm(pos[1])))

pcbnew.SaveBoard(pcb_path, board)
print("Silkscreen text corrected.")
