import pcbnew

PCB_PATH = 'build/icio500/icio500.kicad_pcb'
b = pcbnew.LoadBoard(PCB_PATH)

for d in b.GetDrawings():
    layer = b.GetLayerName(d.GetLayer())
    if layer == 'F.Silkscreen' and type(d) is pcbnew.PCB_SHAPE:
        # Find DIGITAL PROCESSING box (was roughly 51, 131 to 140, 160)
        start_x = d.GetStart().x / 1e6
        start_y = d.GetStart().y / 1e6
        
        if 49 < start_x < 53 and 129 < start_y < 133:
            # Found it. Expand Y to 125
            d.SetStart(pcbnew.VECTOR2I(d.GetStart().x, int(125 * 1e6)))
            # Re-verify and save
            break

for d in b.GetDrawings():
    layer = b.GetLayerName(d.GetLayer())
    if layer == 'F.Silkscreen' and type(d) is pcbnew.PCB_TEXT:
        if d.GetText() == 'DIGITAL PROCESSING':
            d.SetPosition(pcbnew.VECTOR2I(int(53 * 1e6), int(127 * 1e6)))

pcbnew.SaveBoard(PCB_PATH, b)
print("Expanded DIGITAL PROCESSING box.")
