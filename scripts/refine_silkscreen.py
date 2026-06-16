import pcbnew

b = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

# 1. Clean up old boxes and titles
drawings_to_remove = []
for d in list(b.GetDrawings()):
    if d.GetLayer() == b.GetLayerID('F.Silkscreen'):
        if type(d) is pcbnew.PCB_SHAPE or type(d) is pcbnew.PCB_TEXT:
            drawings_to_remove.append(d)
for d in drawings_to_remove:
    b.Remove(d)

# 2. Define groups including D1 and D2 in POWER
groups = {
    'LINE DRIVER': ['U4', 'C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26', 'R7', 'R8'],
    'SCALING': ['U3', 'C15', 'C16', 'C17', 'C18', 'R3', 'R4', 'R5', 'R6'],
    'BALANCED INPUT': ['U2', 'C7', 'C8', 'C13', 'C14', 'R1', 'R2', 'D3', 'D4', 'D5', 'D6'],
    'POWER': ['U1', 'C1', 'C2', 'C3', 'C4', 'C9', 'C10', 'C11', 'C12', 'D1', 'D2'],
    'DIGITAL PROCESSING': ['U5', 'U6', 'U7', 'C5', 'C6']
}

# Find footprints manually
fps_dict = {}
for fp in b.GetFootprints():
    fps_dict[fp.GetReference()] = fp

# 3. Calculate bounding boxes with a uniform 2.5mm margin
for name, refs in groups.items():
    min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
    for ref in refs:
        fp = fps_dict.get(ref)
        if fp:
            bb = fp.GetBoundingBox()
            min_x = min(min_x, bb.GetLeft() / 1e6)
            max_x = max(max_x, bb.GetRight() / 1e6)
            min_y = min(min_y, bb.GetTop() / 1e6)
            max_y = max(max_y, bb.GetBottom() / 1e6)
    
    margin = 3.0
    bx1, bx2, by1, by2 = min_x - margin, max_x + margin, min_y - margin, max_y + margin
    
    shape = pcbnew.PCB_SHAPE(b)
    shape.SetShape(pcbnew.SHAPE_T_RECT)
    shape.SetFilled(False)
    shape.SetStart(pcbnew.VECTOR2I(int(bx1*1e6), int(by1*1e6)))
    shape.SetEnd(pcbnew.VECTOR2I(int(bx2*1e6), int(by2*1e6)))
    shape.SetLayer(b.GetLayerID('F.Silkscreen'))
    shape.SetWidth(int(0.2*1e6))
    b.Add(shape)
    
    t = pcbnew.PCB_TEXT(b)
    t.SetText(name)
    t.SetPosition(pcbnew.VECTOR2I(int((bx1 + 1.5)*1e6), int((by1 - 1.5)*1e6)))
    t.SetLayer(b.GetLayerID('F.Silkscreen'))
    t.SetTextSize(pcbnew.VECTOR2I(int(1.2*1e6), int(1.2*1e6)))
    t.SetTextThickness(int(0.2*1e6))
    b.Add(t)

# 4. Fix Silkscreen over copper for references by moving them
for fp in b.GetFootprints():
    ref_field = fp.Reference()
    if ref_field:
        bb = fp.GetBoundingBox()
        # Move reference to the bottom left of the footprint bounding box, slightly outside
        ref_field.SetPosition(pcbnew.VECTOR2I(int(bb.GetLeft()), int(bb.GetBottom() + 1.5*1e6)))
        ref_field.SetTextSize(pcbnew.VECTOR2I(int(0.8*1e6), int(0.8*1e6)))
        ref_field.SetTextThickness(int(0.15*1e6))

b.BuildConnectivity()
pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', b)
print('Silkscreen refined.')
