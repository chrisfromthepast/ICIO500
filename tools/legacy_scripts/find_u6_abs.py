import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
u6 = board.FindFootprintByReference('U6')
if u6:
    print(f"U6 ABSOLUTE: X={u6.GetPosition().x/1e6}, Y={u6.GetPosition().y/1e6}")
else:
    print("Not found")
