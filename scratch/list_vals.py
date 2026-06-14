import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
for m in board.GetFootprints():
    if m.GetReference().startswith('C') or m.GetReference().startswith('R'):
        print(f"{m.GetReference()}: {m.GetValue()}")
