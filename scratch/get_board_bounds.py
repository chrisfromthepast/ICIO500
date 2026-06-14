import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
min_x, min_y, max_x, max_y = 1e9, 1e9, -1e9, -1e9
for dwg in board.GetDrawings():
    if dwg.GetLayer() == pcbnew.Edge_Cuts:
        box = dwg.GetBoundingBox()
        min_x = min(min_x, box.GetX())
        min_y = min(min_y, box.GetY())
        max_x = max(max_x, box.GetRight())
        max_y = max(max_y, box.GetBottom())
print(f"Edge.Cuts Bounds: X: {min_x/1e6:.1f} to {max_x/1e6:.1f}, Y: {min_y/1e6:.1f} to {max_y/1e6:.1f}")
