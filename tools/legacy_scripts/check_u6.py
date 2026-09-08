import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
u6 = board.FindFootprintByReference('U6')
print(f"U6 position: {u6.GetPosition().x / 1e6}, {u6.GetPosition().y / 1e6}")
for pad in u6.Pads():
    print(f"Pad {pad.GetPadName()} at {pad.GetPosition().x / 1e6}, {pad.GetPosition().y / 1e6}")
