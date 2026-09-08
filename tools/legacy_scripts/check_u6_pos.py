import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
for fp in board.GetFootprints():
    if fp.GetReference() == 'U6':
        print("U6 position:", fp.GetPosition().x/1e6, fp.GetPosition().y/1e6)
        print("U6 rotation:", fp.GetOrientationDegrees())
        print("U6 layer:", board.GetLayerName(fp.GetLayer()))
