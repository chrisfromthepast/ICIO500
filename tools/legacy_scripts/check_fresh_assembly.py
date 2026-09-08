import pcbnew
try:
    board = pcbnew.LoadBoard('build/icio500/icio500_3d_assembly.kicad_pcb')
    u6 = board.FindFootprintByReference('U6')
    if u6:
        print(f"U6 is at X={u6.GetPosition().x/1e6}, Y={u6.GetPosition().y/1e6}")
    else:
        print("U6 not found by ref, trying all footprints...")
        for fp in board.GetFootprints():
            if 'U6' in fp.GetReference():
                print(f"Found {fp.GetReference()} at X={fp.GetPosition().x/1e6}, Y={fp.GetPosition().y/1e6}")
except Exception as e:
    print("Error loading board:", e)
