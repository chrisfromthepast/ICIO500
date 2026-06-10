import pcbnew
import os
import sys

pcb_path = os.path.join("build", "icio500", "icio500.kicad_pcb")
board = pcbnew.LoadBoard(pcb_path)

def move(ref, x, y, rot=0):
    fp = board.FindFootprintByReference(ref)
    if fp:
        fp.SetPosition(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)))
        fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
        if fp.IsFlipped():
            fp.Flip(fp.GetPosition(), False)

# 1. DC-DC Converter (U1) and its caps (C5, C6)
# Move to top edge
u1_x, u1_y = 120.0, 65.0
move('U1', u1_x, u1_y, 0)
move('C5', u1_x - 5.0, u1_y - 2.0, 90)
move('C6', u1_x + 5.0, u1_y - 2.0, 90)

# 2. VCA (U3) and its passives (R6, R7, R8, C25, C26, C17, C18)
# U3 is at X=165, Y=90
u3_x, u3_y = 165.0, 90.0
move('U3', u3_x, u3_y, 0)
# Place passives tightly around U3
move('R6', u3_x - 5.0, u3_y - 3.0, 90)
move('R7', u3_x - 5.0, u3_y + 3.0, 90)
move('R8', u3_x + 5.0, u3_y - 3.0, 90)
move('C25', u3_x + 5.0, u3_y + 3.0, 90)
move('C26', u3_x - 8.0, u3_y - 3.0, 90)
move('C17', u3_x - 8.0, u3_y + 3.0, 90)
move('C18', u3_x + 8.0, u3_y - 3.0, 90)

# 3. Input power filtering (D1, D2, C2, C4)
# Move near the bottom right edge connector
pwr_x, pwr_y = 180.0, 145.0
move('D1', pwr_x, pwr_y, 0)
move('C2', pwr_x + 5.0, pwr_y, 90)
move('D2', pwr_x, pwr_y + 5.0, 0)
move('C4', pwr_x + 5.0, pwr_y + 5.0, 90)

# 4. Headers (U6, U7)
hdr_x, hdr_y = 120.0, 145.0
move('U6', hdr_x, hdr_y, 0)
move('U7', hdr_x + 5.0, hdr_y, 0)

# 5. Daisy Seed (U5)
# Place vertically
move('U5', 90.0, 105.0, 90)

pcbnew.SaveBoard(pcb_path, board)
print("Remaining components placed and tightened.")
sys.exit(0)
