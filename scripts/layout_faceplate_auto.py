import pcbnew
import math

board_path = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\faceplate\faceplate.kicad_pcb"
board = pcbnew.LoadBoard(board_path)

# Clear existing Edge.Cuts
for dwg in board.GetDrawings():
    if dwg.GetLayer() == pcbnew.Edge_Cuts:
        board.Remove(dwg)

# Draw 500-series outline: 38.1mm x 133.35mm
def add_line(x1, y1, x2, y2):
    line = pcbnew.PCB_SHAPE(board)
    line.SetShape(pcbnew.SHAPE_T_SEGMENT)
    line.SetLayer(pcbnew.Edge_Cuts)
    line.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
    line.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
    line.SetWidth(pcbnew.FromMM(0.15))
    board.Add(line)

add_line(0, 0, 38.1, 0)
add_line(38.1, 0, 38.1, 133.35)
add_line(38.1, 133.35, 0, 133.35)
add_line(0, 133.35, 0, 0)

# Layout components
def move_comp(ref, x, y, flip=False, angle=0):
    fp = board.FindFootprintByReference(ref)
    if fp:
        if flip and fp.GetLayer() == pcbnew.F_Cu:
            fp.Flip(fp.GetPosition(), False)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        fp.SetOrientation(pcbnew.EDA_ANGLE(angle, pcbnew.DEGREES_T))

# Faceplate front components (F.Cu)
move_comp("U8", 19.05, 110) # D-Series connector at bottom
move_comp("U3", 19.05, 45)  # Encoder above center

# LEDs in a vertical line above the encoder
move_comp("U4", 19.05, 15)  # Clip (Red)
move_comp("U5", 19.05, 20)  # Amber
move_comp("U6", 19.05, 25)  # Green
move_comp("U7", 19.05, 30)  # Blue

# Back components (B.Cu)
# Move Header U1 to the back, facing the mainboard
move_comp("U1", 19.05, 75, flip=True)

# Move IC and passives to the back, around the header
move_comp("U2", 19.05, 65, flip=True)

# Just cluster the rest of the Rs and Cs on the back near the IC
passive_y = 60
for ref in ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "C1", "C2", "C3"]:
    move_comp(ref, 10 + (int(ref[1:])%4)*5, passive_y + (int(ref[1:])//4)*5, flip=True)

board.Save(board_path)
print("Faceplate laid out successfully!")
