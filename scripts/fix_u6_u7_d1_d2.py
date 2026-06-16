import pcbnew

PCB_PATH = 'build/icio500/icio500.kicad_pcb'
b = pcbnew.LoadBoard(PCB_PATH)

# Move U6 and U7 (switches) closer to the right side of the Daisy (U5)
# U5 is at 50, 122.5. The right side is around X=60-70.
# The ratsnest lines show they connect near the middle/top right.
fp_u6 = b.FindFootprintByReference('U6')
if fp_u6:
    fp_u6.SetPosition(pcbnew.VECTOR2I(int(70 * 1e6), int(120 * 1e6)))
    fp_u6.SetOrientationDegrees(0) # Keep orientation standard

fp_u7 = b.FindFootprintByReference('U7')
if fp_u7:
    fp_u7.SetPosition(pcbnew.VECTOR2I(int(70 * 1e6), int(130 * 1e6)))
    fp_u7.SetOrientationDegrees(0)

# Move D1 and D2 (TVS diodes) closer to the Edge Connector (J1)
# J1 is at 198.5, 98.9. D1/D2 connect to J1 pins. Let's put them below J1.
fp_d1 = b.FindFootprintByReference('D1')
if fp_d1:
    fp_d1.SetPosition(pcbnew.VECTOR2I(int(185 * 1e6), int(120 * 1e6)))

fp_d2 = b.FindFootprintByReference('D2')
if fp_d2:
    fp_d2.SetPosition(pcbnew.VECTOR2I(int(185 * 1e6), int(130 * 1e6)))

# Clean up all Dwgs.User elements (boxes and labels) before redrawing
to_remove = []
for d in b.GetDrawings():
    layer = b.GetLayerName(d.GetLayer())
    if layer == 'Dwgs.User':
        if type(d) is pcbnew.PCB_TEXT:
            if d.GetText() in ['LINE DRIVER', 'SCALING', 'BALANCED INPUT', 'POWER', 'DIGITAL PROCESSING', 'EDGE CONNECTOR']:
                to_remove.append(d)
        elif type(d) is pcbnew.PCB_SHAPE:
            # Assumed to be our drawn bounding boxes
            to_remove.append(d)

for d in to_remove:
    b.Remove(d)

b.BuildConnectivity()
pcbnew.SaveBoard(PCB_PATH, b)
print("Moved U6, U7, D1, D2 and cleared old boxes.")
