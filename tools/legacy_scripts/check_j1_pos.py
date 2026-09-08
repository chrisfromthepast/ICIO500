import pcbnew
board = pcbnew.LoadBoard('build/icio500/panel_satellite.kicad_pcb')
j1 = board.FindFootprintByReference('J1')
print("J1 position:", j1.GetPosition().x/1e6, j1.GetPosition().y/1e6)
print("J1 rotation:", j1.GetOrientationDegrees())
print("J1 layer:", board.GetLayerName(j1.GetLayer()))
