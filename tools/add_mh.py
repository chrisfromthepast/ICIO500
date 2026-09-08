import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

mh1 = pcbnew.FootprintLoad('C:/Program Files/KiCad/10.0/share/kicad/footprints/MountingHole.pretty', 'MountingHole_3.2mm_M3')
mh1.SetPosition(pcbnew.VECTOR2I(int(57.17 * 1e6), int(60 * 1e6)))
mh1.SetReference('MH1')
board.Add(mh1)

mh2 = pcbnew.FootprintLoad('C:/Program Files/KiCad/10.0/share/kicad/footprints/MountingHole.pretty', 'MountingHole_3.2mm_M3')
mh2.SetPosition(pcbnew.VECTOR2I(int(57.17 * 1e6), int(164.3 * 1e6)))
mh2.SetReference('MH2')
board.Add(mh2)

pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
print('Added mounting holes!')
