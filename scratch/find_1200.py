import pcbnew

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

# Find the THAT1200 IC
u_1200 = None
for m in board.GetFootprints():
    ref = m.GetReference()
    fp_id = m.GetFPID().GetLibItemName().c_str()
    # Or just check if the reference is Usomething and it's near the BALANCED INPUT box, or check the netlist
    print(f"{ref}: {fp_id}")
