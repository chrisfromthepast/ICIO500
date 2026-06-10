import pcbnew
import os

pcb_path = os.path.join("build", "icio500", "icio500.kicad_pcb")
board = pcbnew.LoadBoard(pcb_path)

def mm(v): return int(v * 1e6)

ic_values = {
    'U1': 'DC-DC ISO',
    'U2': 'THAT1200',
    'U3': 'TL072',
    'U4': 'THAT1646',
    'U5': 'Daisy Seed',
}

ic_positions = {
    'U1': (125.25, 86.5),  # Bottom of Isolated Power box
    'U2': (174.0, 110.0),  # Right of U2 (Input Stage)
    'U3': (174.0, 90.0),   # Right of U3 (Level Scaling)
    'U4': (174.0, 70.0),   # Right of U4 (Output Stage)
    'U5': (100.0, 160.0),  # Bottom center of Daisy Digital box
}

for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref in ic_values:
        val = fp.Value()
        val.SetText(ic_values[ref])
        val.SetVisible(True)
        val.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
        val.SetTextThickness(mm(0.12))
        val.SetLayer(pcbnew.F_SilkS)
        
        pos = ic_positions[ref]
        val.SetPosition(pcbnew.VECTOR2I(mm(pos[0]), mm(pos[1])))

pcbnew.SaveBoard(pcb_path, board)
print("IC values injected safely.")
