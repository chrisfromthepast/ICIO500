import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
U2 = board.FindFootprintByReference('U2')
print(f"U2 Position: {U2.GetPosition().x/1e6}, {U2.GetPosition().y/1e6}")
for pad in U2.Pads():
    print(f"Pin {pad.GetPadName()}: {pad.GetPosition().x/1e6}, {pad.GetPosition().y/1e6}")
