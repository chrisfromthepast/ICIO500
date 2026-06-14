import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
for m in board.GetFootprints():
    path = m.GetPath().AsString()
    if "receiver" in path:
        print(f"{m.GetReference()}: {path}")
