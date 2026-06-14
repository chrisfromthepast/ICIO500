import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
for dwg in board.GetDrawings():
    if dwg.GetLayer() == pcbnew.Edge_Cuts:
        if isinstance(dwg, pcbnew.PCB_SHAPE):
            print(f"Shape: ({dwg.GetStartX()/1e6:.1f}, {dwg.GetStartY()/1e6:.1f}) to ({dwg.GetEndX()/1e6:.1f}, {dwg.GetEndY()/1e6:.1f})")
