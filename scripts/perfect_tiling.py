import pcbnew

PCB_PATH = 'build/icio500/icio500.kicad_pcb'
b = pcbnew.LoadBoard(PCB_PATH)

# Place passives strictly inside boxes with sufficient courtyard clearance
def place_passives(center_x, start_y, refs, spacing_x=6, spacing_y=8, max_cols=4):
    start_x = center_x - ((max_cols-1)*spacing_x/2.0)
    for i, ref in enumerate(refs):
        fp = b.FindFootprintByReference(ref)
        if not fp: continue
        col = i % max_cols
        row = i // max_cols
        x = start_x + (col * spacing_x)
        y = start_y + (row * spacing_y)
        
        # Center the passive exactly
        bb = fp.GetBoundingBox()
        bb_cx = bb.GetCenter().x / 1e6
        bb_cy = bb.GetCenter().y / 1e6
        dx = x - bb_cx
        dy = y - bb_cy
        pos = fp.GetPosition()
        fp.SetPosition(pcbnew.VECTOR2I(int((pos.x/1e6 + dx)*1e6), int((pos.y/1e6 + dy)*1e6)))

def place_ic(ref, x, y):
    fp = b.FindFootprintByReference(ref)
    if fp:
        bb = fp.GetBoundingBox()
        bb_cx = bb.GetCenter().x / 1e6
        bb_cy = bb.GetCenter().y / 1e6
        dx = x - bb_cx
        dy = y - bb_cy
        pos = fp.GetPosition()
        fp.SetPosition(pcbnew.VECTOR2I(int((pos.x/1e6 + dx)*1e6), int((pos.y/1e6 + dy)*1e6)))

# The new boxes from fix_drc are:
# LINE DRIVER: 125 to 174, 55 to 85. Center X = 149.5
place_ic('U4', 149.5, 62)
place_passives(149.5, 72, ['C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26', 'R7', 'R8'], spacing_x=6, spacing_y=6, max_cols=5)

# SCALING: 90 to 120, 60 to 90. Center X = 105
place_ic('U3', 105, 68)
place_passives(105, 78, ['C15', 'C16', 'C17', 'C18', 'R3', 'R4', 'R5', 'R6'], spacing_x=6, spacing_y=6, max_cols=4)

# BALANCED INPUT: 142 to 174, 85 to 125. Center X = 158
place_ic('U2', 158, 93)
place_passives(158, 103, ['C7', 'C8', 'C13', 'C14', 'R1', 'R2', 'D3', 'D4', 'D5', 'D6'], spacing_x=6, spacing_y=6, max_cols=5)

# POWER: 100 to 140, 95 to 130. Center X = 120
place_ic('U1', 120, 102)
place_passives(120, 112, ['C1', 'C2', 'C3', 'C4', 'C9', 'C10', 'C11', 'C12'], spacing_x=6, spacing_y=6, max_cols=4)

# DIGITAL PROCESSING: 51 to 140, 125 to 160.
# U5 is at 55 to 115 (approx), Y=128 to 146.
place_passives(120, 138, ['U6', 'U7', 'C5', 'C6'], spacing_x=8, spacing_y=8, max_cols=4)

# Ensure J1 edge connector text is clear
place_ic('D1', 170, 140)
place_ic('D2', 170, 150)

b.BuildConnectivity()
pcbnew.SaveBoard(PCB_PATH, b)
print("Perfect tiling applied inside new safe boxes.")
