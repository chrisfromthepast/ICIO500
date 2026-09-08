import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
for fp in board.GetFootprints():
    if fp.GetFPIDAsString() == 'Cards:EDA_306':
        print("Main footprint position:", fp.GetPosition().x/1e6, fp.GetPosition().y/1e6)
