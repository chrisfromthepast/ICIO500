import pcbnew
import sys
with open('u6_pads.txt', 'w') as f:
    board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
    u6 = board.FindFootprintByReference('U6')
    f.write(f"U6 position: {u6.GetPosition().x / 1e6}, {u6.GetPosition().y / 1e6}\n")
    for pad in u6.Pads():
        f.write(f"Pad {pad.GetPadName()} at {pad.GetPosition().x / 1e6}, {pad.GetPosition().y / 1e6}\n")
