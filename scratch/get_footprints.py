import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
for ref in ['C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26', 'R7', 'R8']:
    fp = board.FindFootprintByReference(ref)
    print(f"{ref}: {fp.GetFPID().GetLibItemName().c_str()}")
