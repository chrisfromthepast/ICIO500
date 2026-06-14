import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
for ref in ['U2', 'U3']:
    fp = board.FindFootprintByReference(ref)
    print(f"{ref}: {fp.GetValue()}")
