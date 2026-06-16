import pcbnew

PCB_PATH = 'build/icio500/icio500.kicad_pcb'
b = pcbnew.LoadBoard(PCB_PATH)

# Move U6 and U7 (the two switches) closer to U5 (the Daisy)
# U5 is at (50, 122.5)
fp_u6 = b.FindFootprintByReference('U6')
if fp_u6:
    fp_u6.SetPosition(pcbnew.VECTOR2I(int(50 * 1e6), int(152 * 1e6)))

fp_u7 = b.FindFootprintByReference('U7')
if fp_u7:
    fp_u7.SetPosition(pcbnew.VECTOR2I(int(60 * 1e6), int(152 * 1e6)))

# Move D1 and D2 (TVS diodes) so they are on the board
# Bottom edge is Y=160
fp_d1 = b.FindFootprintByReference('D1')
if fp_d1:
    fp_d1.SetPosition(pcbnew.VECTOR2I(int(185 * 1e6), int(145 * 1e6)))

fp_d2 = b.FindFootprintByReference('D2')
if fp_d2:
    fp_d2.SetPosition(pcbnew.VECTOR2I(int(185 * 1e6), int(150 * 1e6)))

# Clear old labels
to_remove = []
for d in b.GetDrawings():
    layer = b.GetLayerName(d.GetLayer())
    if layer == 'Dwgs.User':
        if type(d) is pcbnew.PCB_TEXT:
            if d.GetText() in ['LINE DRIVER', 'SCALING', 'BALANCED INPUT', 'POWER', 'DIGITAL PROCESSING', 'EDGE CONNECTOR']:
                to_remove.append(d)
        elif type(d) is pcbnew.PCB_SHAPE:
            # Check if it's a rectangle we drew
            to_remove.append(d)

for d in to_remove:
    b.Remove(d)

b.BuildConnectivity()
pcbnew.SaveBoard(PCB_PATH, b)
print("Moved pairs and cleared old boxes.")
