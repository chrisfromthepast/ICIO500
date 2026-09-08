import pcbnew
board = pcbnew.LoadBoard('build/icio500/temp.kicad_pcb')
mh1 = board.FindFootprintByReference('MH1')
mh2 = board.FindFootprintByReference('MH2')
print(f'MH1 pos: {mh1.GetPosition()}')
print(f'MH2 pos: {mh2.GetPosition()}')
