import pcbnew; b=pcbnew.LoadBoard('build/icio500/icio500_3d_assembly.kicad_pcb'); print('DUMMY footprint found:', b.FindFootprintByReference('DUMMY') is not None)
