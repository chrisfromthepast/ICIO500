import pcbnew
import sys
import os

pcb_path = os.path.join("build", "icio500", "icio500.kicad_pcb")
board = pcbnew.LoadBoard(pcb_path)

def mm(v): return int(v * 1_000_000)

SHIFT_Y = -12.0 # Move up by 12mm

components = ["U5", "U6", "U7", "J6", "J7"]

# Move components
for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref in components:
        pos = fp.GetPosition()
        fp.SetPosition(pcbnew.VECTOR2I(pos.x, pos.y + mm(SHIFT_Y)))
        
# Move silkscreen text "DAISY DIGITAL"
for d in board.GetDrawings():
    if isinstance(d, pcbnew.PCB_TEXT):
        if d.GetText() == "DAISY DIGITAL":
            pos = d.GetPosition()
            d.SetPosition(pcbnew.VECTOR2I(pos.x, pos.y + mm(SHIFT_Y)))
    
    # We also have a bounding box for DAISY DIGITAL.
    # It was drawn with PCB_SHAPE on F.SilkS in the area roughly X: 82 to 117, Y: 101 to 162.
    # We will move ANY shape on F.SilkS that falls within that area.
    if isinstance(d, pcbnew.PCB_SHAPE) and d.GetLayerName() == 'F.SilkS':
        start = d.GetStart()
        end = d.GetEnd()
        sx, sy = start.x / 1e6, start.y / 1e6
        # if the shape is in the daisy digital box area
        if 80 < sx < 120 and 95 < sy < 165:
            d.Move(pcbnew.VECTOR2I(0, mm(SHIFT_Y)))

pcbnew.SaveBoard(pcb_path, board)
print("Moved Daisy block up by 12mm.")
sys.exit(0)
