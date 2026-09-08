import pcbnew
b = pcbnew.LoadBoard('build/icio500/panel_satellite.kicad_pcb')
for t in b.GetTracks():
    b.Remove(t)
pcbnew.SaveBoard('build/icio500/panel_satellite.kicad_pcb', b)
