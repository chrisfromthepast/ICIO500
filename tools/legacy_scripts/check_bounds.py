import pcbnew
def get_bbox(filename):
    b = pcbnew.LoadBoard(filename)
    bbox = b.GetBoardEdgesBoundingBox()
    return {
        "x": bbox.GetX() / 1e6,
        "y": bbox.GetY() / 1e6,
        "w": bbox.GetWidth() / 1e6,
        "h": bbox.GetHeight() / 1e6,
        "cx": bbox.GetCenter().x / 1e6,
        "cy": bbox.GetCenter().y / 1e6
    }

print("Main:", get_bbox('build/icio500/icio500.kicad_pcb'))
print("Faceplate:", get_bbox('build/icio500/faceplate_front.kicad_pcb'))
print("Satellite:", get_bbox('build/icio500/panel_satellite.kicad_pcb'))
