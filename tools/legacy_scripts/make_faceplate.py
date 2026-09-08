import pcbnew

b = pcbnew.LoadBoard('build/icio500/faceplate_front.kicad_pcb')

# 1. Add Encoder Hole on Edge.Cuts
# Encoder is at (19.05, 109.35)
hole = pcbnew.PCB_SHAPE(b)
hole.SetShape(pcbnew.SHAPE_T_CIRCLE)
hole.SetLayer(pcbnew.Edge_Cuts)
hole.SetCenter(pcbnew.VECTOR2I_MM(19.05, 109.35))
hole.SetStart(pcbnew.VECTOR2I_MM(19.05, 109.35 + 3.75)) # 7.5mm diameter
hole.SetWidth(pcbnew.FromMM(0.1))
b.Add(hole)

# 2. Add LED Mask openings
# LEDs at Y = 20, 28, 36, 44, 52, 60, 68, 76, 84, 92
led_ys = [20, 28, 36, 44, 52, 60, 68, 76, 84, 92]
for y in led_ys:
    for layer in [pcbnew.F_Mask, pcbnew.B_Mask]:
        mask = pcbnew.PCB_SHAPE(b)
        mask.SetShape(pcbnew.SHAPE_T_CIRCLE)
        mask.SetLayer(layer)
        mask.SetCenter(pcbnew.VECTOR2I_MM(19.05, y))
        mask.SetStart(pcbnew.VECTOR2I_MM(19.05, y + 1.5)) # 3mm diameter mask
        # Filled circle
        mask.SetFilled(True)
        mask.SetWidth(0)
        b.Add(mask)

# 3. Add Silkscreen
def add_text(text, x, y, size=1.5, thickness=0.3, layer=pcbnew.F_SilkS):
    t = pcbnew.PCB_TEXT(b)
    t.SetText(text)
    t.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    t.SetTextSize(pcbnew.VECTOR2I_MM(size, size))
    t.SetTextThickness(pcbnew.FromMM(thickness))
    t.SetLayer(layer)
    b.Add(t)

add_text("ICIO 500", 19.05, 15, size=2.5, thickness=0.5)
add_text("LEVEL", 19.05, 118, size=1.5, thickness=0.3)

# Add tick marks for LEDs
db_labels = ["CLIP", "+4", "0", "-4", "-8", "-12", "-16", "-20", "-24", "-30"]
for i, y in enumerate(led_ys):
    add_text(db_labels[i], 12.0, y, size=1.0, thickness=0.2)

pcbnew.SaveBoard('build/icio500/faceplate_front.kicad_pcb', b)
