import pcbnew

PCB_PATH = 'build/icio500/icio500.kicad_pcb'
b = pcbnew.LoadBoard(PCB_PATH)

# Define translation vectors
# POWER center: 145, 100. SCALING center: 170, 140.5
# Delta POWER -> SCALING: dx = 25.0, dy = 40.5
# Delta SCALING -> POWER: dx = -25.0, dy = -40.5
vec_pow_to_scale = pcbnew.VECTOR2I(int(25.0 * 1e6), int(40.5 * 1e6))
vec_scale_to_pow = pcbnew.VECTOR2I(int(-25.0 * 1e6), int(-40.5 * 1e6))

# 1. Swap components
groups = {
    'POWER': ['U1', 'C1', 'C2', 'C3', 'C4', 'C9', 'C10', 'C11', 'C12'],
    'SCALING': ['U3', 'C15', 'C16', 'C17', 'C18', 'R3', 'R4', 'R5', 'R6']
}

for ref in groups['POWER']:
    fp = b.FindFootprintByReference(ref)
    if fp:
        pos = fp.GetPosition()
        fp.SetPosition(pcbnew.VECTOR2I(pos.x + vec_pow_to_scale.x, pos.y + vec_pow_to_scale.y))

for ref in groups['SCALING']:
    fp = b.FindFootprintByReference(ref)
    if fp:
        pos = fp.GetPosition()
        fp.SetPosition(pcbnew.VECTOR2I(pos.x + vec_scale_to_pow.x, pos.y + vec_scale_to_pow.y))

# 2. Swap F.Silkscreen boxes and texts
for d in b.GetDrawings():
    layer = b.GetLayerName(d.GetLayer())
    if layer == 'F.Silkscreen':
        if type(d) is pcbnew.PCB_SHAPE:
            start_x = d.GetStart().x / 1e6
            start_y = d.GetStart().y / 1e6
            end_x = d.GetEnd().x / 1e6
            end_y = d.GetEnd().y / 1e6
            
            # Identify POWER box (roughly 130, 85 to 160, 115)
            if 125 < start_x < 135 and 80 < start_y < 90:
                d.SetStart(pcbnew.VECTOR2I(d.GetStart().x + vec_pow_to_scale.x, d.GetStart().y + vec_pow_to_scale.y))
                d.SetEnd(pcbnew.VECTOR2I(d.GetEnd().x + vec_pow_to_scale.x, d.GetEnd().y + vec_pow_to_scale.y))
            # Identify SCALING box (roughly 155, 126 to 185, 155)
            elif 150 < start_x < 160 and 120 < start_y < 130:
                d.SetStart(pcbnew.VECTOR2I(d.GetStart().x + vec_scale_to_pow.x, d.GetStart().y + vec_scale_to_pow.y))
                d.SetEnd(pcbnew.VECTOR2I(d.GetEnd().x + vec_scale_to_pow.x, d.GetEnd().y + vec_scale_to_pow.y))

        elif type(d) is pcbnew.PCB_TEXT:
            if d.GetText() == 'POWER':
                pos = d.GetPosition()
                d.SetPosition(pcbnew.VECTOR2I(pos.x + vec_pow_to_scale.x, pos.y + vec_pow_to_scale.y))
            elif d.GetText() == 'SCALING':
                pos = d.GetPosition()
                d.SetPosition(pcbnew.VECTOR2I(pos.x + vec_scale_to_pow.x, pos.y + vec_scale_to_pow.y))

b.BuildConnectivity()
pcbnew.SaveBoard(PCB_PATH, b)
print("Swapped POWER and SCALING blocks and silkscreens.")
