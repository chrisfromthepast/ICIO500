import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
U3 = board.FindFootprintByReference('U3')
print(f"U3 Position: {U3.GetPosition().x/1e6}, {U3.GetPosition().y/1e6}")
for pad in U3.Pads():
    print(f"Pin {pad.GetPadName()}: {pad.GetPosition().x/1e6}, {pad.GetPosition().y/1e6}")
