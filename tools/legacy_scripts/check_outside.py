import pcbnew
board = pcbnew.LoadBoard('build/icio500/panel_satellite.kicad_pcb')
for fp in board.GetFootprints():
    x = fp.GetPosition().x/1e6
    if x < 100:
        print(f"Footprint {fp.GetReference()} is at {x} (outside edge!)")
