import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
r8 = board.FindFootprintByReference('R8')
u2 = board.FindFootprintByReference('U2')
if r8: print("R8 p2:", r8.FindPadByNumber("2").GetPosition())
if u2: print("U2 p7:", u2.FindPadByNumber("7").GetPosition())
