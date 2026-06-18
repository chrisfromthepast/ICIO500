import pcbnew
import os

# Create directory
if not os.path.exists("faceplate"):
    os.makedirs("faceplate")

# Create a new empty board
board = pcbnew.BOARD()

MM = 1e6
WIDTH = 38.1 * MM
HEIGHT = 133.35 * MM

def draw_line(x1, y1, x2, y2, layer, width=0.15):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(layer)
    seg.SetStart(pcbnew.VECTOR2I(int(x1), int(y1)))
    seg.SetEnd(pcbnew.VECTOR2I(int(x2), int(y2)))
    seg.SetWidth(int(width * MM))
    board.Add(seg)

def draw_circle(x, y, radius, layer):
    circle = pcbnew.PCB_SHAPE(board)
    circle.SetShape(pcbnew.SHAPE_T_CIRCLE)
    circle.SetLayer(layer)
    circle.SetCenter(pcbnew.VECTOR2I(int(x), int(y)))
    circle.SetStart(pcbnew.VECTOR2I(int(x + radius), int(y)))
    circle.SetWidth(int(0.15 * MM))
    board.Add(circle)

def draw_filled_circle(x, y, radius, layer):
    # Foolproof way to draw a filled circle across KiCad versions: a segment with width = diameter
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(layer)
    seg.SetStart(pcbnew.VECTOR2I(int(x), int(y)))
    seg.SetEnd(pcbnew.VECTOR2I(int(x + 0.01 * MM), int(y)))
    seg.SetWidth(int(radius * 2 * MM))
    board.Add(seg)

def draw_filled_rect(x_center, y_center, width, height, layer):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(layer)
    seg.SetStart(pcbnew.VECTOR2I(int(x_center), int(y_center - height/2)))
    seg.SetEnd(pcbnew.VECTOR2I(int(x_center), int(y_center + height/2)))
    seg.SetWidth(int(width * MM))
    board.Add(seg)

# ---------------------------------------------------------
# Edge Cuts (Physical Outline)
# ---------------------------------------------------------
draw_line(0, 0, WIDTH, 0, pcbnew.Edge_Cuts)
draw_line(WIDTH, 0, WIDTH, HEIGHT, pcbnew.Edge_Cuts)
draw_line(WIDTH, HEIGHT, 0, HEIGHT, pcbnew.Edge_Cuts)
draw_line(0, HEIGHT, 0, 0, pcbnew.Edge_Cuts)

# 500-Series Mounting Holes - 3.8mm diameter (radius 1.9mm)
draw_circle(WIDTH/2, 4.75 * MM, 1.9 * MM, pcbnew.Edge_Cuts)
draw_circle(WIDTH/2, HEIGHT - 4.75 * MM, 1.9 * MM, pcbnew.Edge_Cuts)

# Rotary Encoder Cutout - 7.5mm diameter (radius 3.75mm)
draw_circle(WIDTH/2, 25.0 * MM, 3.75 * MM, pcbnew.Edge_Cuts)

# 4x LED Holes - 2mm diameter (radius 1.0mm)
led_y_start = 45.0
for i in range(4):
    draw_circle(WIDTH/2, (led_y_start + i*5.0) * MM, 1.0 * MM, pcbnew.Edge_Cuts)

# ---------------------------------------------------------
# Exposed Copper / Capacitive Touch Zones
# To expose bare metal, we draw solid F.Cu and F.Mask over it!
# ---------------------------------------------------------

# Middle Geometric Touch Zones
# Drawing two sleek rectangles for touch zones
draw_filled_rect(WIDTH/2, 75.0, 20.0, 6.0, pcbnew.F_Cu)
draw_filled_rect(WIDTH/2, 75.0, 20.0, 6.0, pcbnew.F_Mask)

draw_filled_rect(WIDTH/2, 85.0, 20.0, 6.0, pcbnew.F_Cu)
draw_filled_rect(WIDTH/2, 85.0, 20.0, 6.0, pcbnew.F_Mask)

# Bottom Large D-Series Touch Pad (24mm diameter / 12mm radius)
draw_filled_circle(WIDTH/2, 110.0, 12.0, pcbnew.F_Cu)
draw_filled_circle(WIDTH/2, 110.0, 12.0, pcbnew.F_Mask)

# No silkscreen text per the user's request to keep it stark and industrial!

pcbnew.SaveBoard("faceplate/faceplate.kicad_pcb", board)
print("Silver/Copper Faceplate board generated successfully!")
