import pcbnew
import sys

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

# For DIGITAL PROCESSING (Y max is 145)
place_passives(94, 138, ['U6', 'U7', 'C5', 'C6'], spacing_x=8, spacing_y=8, max_cols=4)

# For POWER (Y min is 85, text is at 87, place at 91+)
place_passives(145, 91, ['C1', 'C2', 'C3', 'C4', 'C9', 'C10', 'C11', 'C12'], spacing_x=6, spacing_y=6, max_cols=4)

# For LINE DRIVER (Y min is 57, text is at 55, place at 62+)
place_passives(160, 62, ['R7', 'R8', 'C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26'], spacing_x=6, spacing_y=6, max_cols=5)

# For BALANCED INPUT (Y min is 85, text is at 87, place at 92+)
place_passives(180.5, 92, ['R1', 'R2', 'C7', 'C8', 'C13', 'C14', 'D3', 'D4', 'D5', 'D6'], spacing_x=6, spacing_y=6, max_cols=5)

# For SCALING (Y min is 126, text is at 128, place at 133+)
place_passives(170, 133, ['R3', 'R4', 'R5', 'R6', 'C15', 'C16', 'C17', 'C18'], spacing_x=6, spacing_y=6, max_cols=4)

b.BuildConnectivity()
pcbnew.SaveBoard(PCB_PATH, b)
print("Spaced out passives perfectly.")
