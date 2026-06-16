import pcbnew

PCB_PATH = 'build/icio500/icio500.kicad_pcb'
b = pcbnew.LoadBoard(PCB_PATH)

groups = {
    'LINE DRIVER': ['U4', 'C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26', 'R7', 'R8'],
    'SCALING': ['U3', 'C15', 'C16', 'C17', 'C18', 'R3', 'R4', 'R5', 'R6'],
    'BALANCED INPUT': ['U2', 'C7', 'C8', 'C13', 'C14', 'R1', 'R2', 'D3', 'D4', 'D5', 'D6'],
    'POWER': ['U1', 'C1', 'C2', 'C3', 'C4', 'C9', 'C10', 'C11', 'C12'],
    'DIGITAL PROCESSING': ['U6', 'U7', 'U5', 'C5', 'C6'],
    'EDGE CONNECTOR': ['J1', 'D1', 'D2']
}

# Find which components are not in any group
assigned = set()
for g, refs in groups.items():
    assigned.update(refs)

unassigned = []
for fp in b.GetFootprints():
    if fp.GetReference() not in assigned:
        unassigned.append(fp.GetReference())

print("Unassigned components:", unassigned)

margin = int(2.5 * 1e6) # 2.5mm margin
text_size = pcbnew.VECTOR2I(int(1.5 * 1e6), int(1.5 * 1e6))
text_thickness = int(0.3 * 1e6)
line_thickness = int(0.15 * 1e6)
layer = pcbnew.Dwgs_User

for name, refs in groups.items():
    fps = [b.FindFootprintByReference(ref) for ref in refs if b.FindFootprintByReference(ref)]
    if not fps:
        continue
    
    # Calculate bounding box of all footprints in the group
    min_x = min([fp.GetBoundingBox().GetLeft() for fp in fps])
    max_x = max([fp.GetBoundingBox().GetRight() for fp in fps])
    min_y = min([fp.GetBoundingBox().GetTop() for fp in fps])
    max_y = max([fp.GetBoundingBox().GetBottom() for fp in fps])
    
    # Draw rectangle
    rect = pcbnew.PCB_SHAPE(b)
    rect.SetShape(pcbnew.SHAPE_T_RECT)
    rect.SetLayer(layer)
    rect.SetWidth(line_thickness)
    rect.SetStart(pcbnew.VECTOR2I(min_x - margin, min_y - margin))
    rect.SetEnd(pcbnew.VECTOR2I(max_x + margin, max_y + margin))
    b.Add(rect)
    
    # Draw text label
    text = pcbnew.PCB_TEXT(b)
    text.SetText(name)
    text.SetLayer(layer)
    text.SetTextSize(text_size)
    text.SetTextThickness(text_thickness)
    text.SetPosition(pcbnew.VECTOR2I(min_x - margin + int(1e6), min_y - margin - int(1.5 * 1e6)))
    text.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    b.Add(text)

b.BuildConnectivity()
pcbnew.SaveBoard(PCB_PATH, b)
print("Added labels and boxes.")
