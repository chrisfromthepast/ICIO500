import pcbnew
import math

b = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

# 1. Clean up old POWER silkscreen box and text
drawings_to_remove = []
for d in list(b.GetDrawings()):
    if d.GetLayer() == b.GetLayerID('F.Silkscreen'):
        if type(d) is pcbnew.PCB_TEXT and d.GetText() == 'POWER':
            drawings_to_remove.append(d)
        elif type(d) is pcbnew.PCB_SHAPE:
            # Check if this box surrounds the old POWER area (e.g. X near 131 to 183)
            if d.GetStart().x / 1e6 > 125 and d.GetStart().y / 1e6 > 110:
                # Wait, BALANCED INPUT is at X=141-176, Y=91-107.
                # D1/D2 caused POWER to be X=131-183, Y=114-150.
                if d.GetStart().y / 1e6 > 110:
                    drawings_to_remove.append(d)

for d in drawings_to_remove:
    b.Remove(d)

# 2. Compact the POWER components into a neat 3-column grid
power_refs = ['U1', 'C1', 'C3', 'D1', 'D2', 'C2', 'C4', 'C12', 'C9', 'C10', 'C11']
base_x = 150.0
base_y = 125.0
spacing_x = 7.0
spacing_y = 6.0

for i, ref in enumerate(power_refs):
    fp = b.FindFootprintByReference(ref)
    if fp:
        col = i % 3
        row = i // 3
        x = base_x + col * spacing_x
        y = base_y + row * spacing_y
        fp.SetPosition(pcbnew.VECTOR2I(int(x*1e6), int(y*1e6)))

# 3. Calculate new perfectly tight bounding box for POWER
min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
for ref in power_refs:
    fp = b.FindFootprintByReference(ref)
    if fp:
        bb = fp.GetBoundingBox()
        min_x = min(min_x, bb.GetLeft() / 1e6)
        max_x = max(max_x, bb.GetRight() / 1e6)
        min_y = min(min_y, bb.GetTop() / 1e6)
        max_y = max(max_y, bb.GetBottom() / 1e6)

margin = 2.5
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
t.SetText('POWER')
t.SetPosition(pcbnew.VECTOR2I(int((bx1 + 1.5)*1e6), int((by1 - 1.5)*1e6)))
t.SetLayer(b.GetLayerID('F.Silkscreen'))
t.SetTextSize(pcbnew.VECTOR2I(int(1.2*1e6), int(1.2*1e6)))
t.SetTextThickness(int(0.2*1e6))
b.Add(t)

# Fix silkscreen over copper for reference labels
for ref in power_refs:
    fp = b.FindFootprintByReference(ref)
    if fp:
        ref_field = fp.Reference()
        if ref_field:
            bb = fp.GetBoundingBox()
            ref_field.SetPosition(pcbnew.VECTOR2I(int(bb.GetLeft()), int(bb.GetBottom() + 1.5*1e6)))
            ref_field.SetTextSize(pcbnew.VECTOR2I(int(0.8*1e6), int(0.8*1e6)))
            ref_field.SetTextThickness(int(0.15*1e6))

# Clear routing because we moved components!
for tr in list(b.Tracks()):
    b.Remove(tr)
for zn in list(b.Zones()):
    b.Remove(zn)

b.BuildConnectivity()
pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', b)
print("POWER block compacted successfully.")
