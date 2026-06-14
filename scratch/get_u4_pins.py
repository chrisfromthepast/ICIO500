import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
u4 = board.FindFootprintByReference('U4')
print(f"U4 Position: {u4.GetPosition().x/1e6}, {u4.GetPosition().y/1e6}")
for pad in u4.Pads():
    print(f"Pin {pad.GetPadName()}: {pad.GetPosition().x/1e6}, {pad.GetPosition().y/1e6}")
