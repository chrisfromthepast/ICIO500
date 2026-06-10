import pcbnew
import os
import sys

pcb_path = os.path.join("build", "icio500", "icio500.kicad_pcb")
board = pcbnew.LoadBoard(pcb_path)

def to_mm(v): return v / 1_000_000

u2 = board.FindFootprintByReference('U2')
if not u2:
    sys.exit(1)
    
u2_x, u2_y = to_mm(u2.GetPosition().x), to_mm(u2.GetPosition().y)

for track in list(board.GetTracks()):
    tx, ty = to_mm(track.GetStart().x), to_mm(track.GetStart().y)
    if u2_x - 35 < tx < u2_x + 15 and u2_y - 20 < ty < u2_y + 20:
        board.Remove(track)

def move(ref, x, y, rot=0):
    fp = board.FindFootprintByReference(ref)
    if fp:
        fp.SetPosition(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)))
        fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
        if fp.IsFlipped():
            fp.Flip(fp.GetPosition(), False)

x, y = 165.0, 110.0
move('U2', x, y, 0)

# C14 (Cboot) bridges Pin 5 and Pin 6 on the right.
move('C14', x + 5.0, y + 1.27, 90)

# V+ and V- decoupling (Pin 8 and Pin 4)
move('C15', x + 5.0, y - 1.9, 90) # Top Right
move('C16', x - 5.0, y + 1.9, 90) # Bottom Left
# Bulk caps C7, C8 on the right side to avoid blocking input path
move('C7', x + 10.0, y - 1.9, 90)
move('C8', x + 10.0, y + 1.9, 90)

# Clamping Diodes (SOD-123). Place them vertically, stacked.
move('D6', x - 9.0, y - 9.0, 90)
move('D5', x - 9.0, y - 3.0, 90)
move('D3', x - 9.0, y + 3.0, 90)
move('D4', x - 9.0, y + 9.0, 90)

# AC Coupling (C13, C12)
move('C13', x - 14.0, y - 5.0, 0)
move('C12', x - 14.0, y + 8.0, 0)

# RF Resistors (R1, R2)
move('R2', x - 19.0, y - 5.0, 0)
move('R1', x - 19.0, y + 8.0, 0)

# RF Caps (C9, C10, C11)
move('C9', x - 23.0, y + 1.5, 90) # Between the two lines
move('C11', x - 25.0, y - 5.0, 0)
move('C10', x - 25.0, y + 8.0, 0)

pcbnew.SaveBoard(pcb_path, board)
print("THAT1200 layout positioned perfectly.")
sys.exit(0)
