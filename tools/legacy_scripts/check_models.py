import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500_3d_assembly.kicad_pcb')
for fp in board.GetFootprints():
    if fp.GetReference() == "DUMMY":
        for model in fp.Models():
            print(f"Model: {model.m_Filename}")
            print(f"  Offset: {model.m_Offset}")
            print(f"  Rotation: {model.m_Rotation}")
