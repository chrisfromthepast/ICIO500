import pcbnew
import math

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

def place(ref, x, y, rot=0):
    fp = board.FindFootprintByReference(ref)
    if fp:
        fp.SetPosition(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)))
        fp.SetOrientationDegrees(rot)

# Remove old text to avoid duplicates first to avoid Kicad 10 SWIG bug
bad_labels = ["BALANCED INPUT STAGE", "LINE DRIVER STAGE", 
              "SCALING & SHIFTING", "POWER CONDITIONING",
              "POWER / REGS", "GAIN TRIM RESISTOR",
              "POWER", "INPUT", "SCALING", "DRIVER", "DAISY SEED"]
try:
    for dwg in list(board.Drawings()):
        if isinstance(dwg, pcbnew.PCB_TEXT) and dwg.GetText() in bad_labels:
            board.Remove(dwg)
except Exception as e:
    print(f"Warning: could not delete drawings: {e}")

# Track deletion moved to end

# ==========================================================
# 1. POWER SUPPLY (Centrally located per user request)
# ==========================================================
# Placed around Y=65 to Y=85, center of the board
place("U1", 145, 75, 0)      # DC-DC Converter in the center
place("C1", 135, 70, 0)      # Bulk + near U1 input
place("C3", 135, 80, 0)      # Bulk - near U1 input
place("C2", 140, 70, 0)      # Cer + near U1 input
place("C4", 140, 80, 0)      # Cer - near U1 input
place("C5", 155, 70, 0)      # Iso + near U1 output
place("C6", 155, 80, 0)      # Iso cer near U1 output
# Protection Diodes right near the edge connector J1 (Y=98)
place("D1", 185, 85, 0)
place("D2", 185, 110, 0)

# ==========================================================
# 2. BALANCED INPUT (Right side, near Edge connector)
# ==========================================================
place("U2", 175, 95, 0)      # Input receiver
place("R1", 185, 90, 0)      # Input resistors
place("R2", 185, 100, 0)
place("C12", 180, 90, 0)     # AC coupling
place("C13", 180, 100, 0)
place("C14", 170, 95, 90)    # Bootstrap
place("C9",  183, 95, 90)    # RF cap
place("C10", 188, 88, 0)     # Chassis shunt
place("C11", 188, 102, 0)
# Diodes spaced neatly
place("D3", 170, 85, 0)
place("D4", 175, 85, 0)
place("D5", 170, 105, 0)
place("D6", 175, 105, 0)
# Bypasses
place("C7", 175, 89, 90)
place("C15", 172, 89, 90)
place("C8", 175, 101, 90)
place("C16", 172, 101, 90)

# ==========================================================
# 3. SCALING & SHIFTING (Center-left)
# ==========================================================
place("U3", 145, 115, 0)
place("R3", 153, 110, 0)
place("R4", 153, 113, 0)
place("R5", 153, 117, 0)
place("R6", 153, 120, 0)
place("C17", 140, 110, 90)
place("C18", 140, 120, 90)

# ==========================================================
# 4. LINE DRIVER (Top, above power)
# ==========================================================
place("U4", 145, 45, 0)
place("C19", 153, 42, 90)
place("C20", 156, 42, 90)
place("C21", 153, 48, 90)
place("C22", 156, 48, 90)
place("C23", 138, 38, 0)
place("C24", 138, 52, 0)
place("R7", 130, 38, 0)
place("C25", 123, 38, 0)
place("R8", 130, 52, 0)
place("C26", 123, 52, 0)

# ==========================================================
# 5. DIGITAL PROCESSING (Far left)
# ==========================================================
# U5 Daisy Seed is very large. Place it clear of other components.
place("U5", 80, 80, 90)      # Daisy Seed
# U6 and U7 placed neatly next to Daisy, not overlapping!
place("U6", 100, 75, 0)
place("U7", 100, 85, 0)

# ==========================================================
# Add Silkscreen Labels and Boxes
# ==========================================================
def add_label(text, x, y):
    txt = pcbnew.PCB_TEXT(board)
    txt.SetText(text)
    txt.SetPosition(pcbnew.VECTOR2I(int(x*1e6), int(y*1e6)))
    txt.SetTextSize(pcbnew.VECTOR2I(int(1.5*1e6), int(1.5*1e6)))
    txt.SetTextThickness(int(0.2*1e6))
    txt.SetLayer(pcbnew.F_SilkS)
    board.Add(txt)

def add_box(x1, y1, x2, y2):
    line = pcbnew.PCB_SHAPE(board)
    line.SetShape(pcbnew.SHAPE_T_RECT)
    line.SetStart(pcbnew.VECTOR2I(int(x1*1e6), int(y1*1e6)))
    line.SetEnd(pcbnew.VECTOR2I(int(x2*1e6), int(y2*1e6)))
    line.SetWidth(int(0.15*1e6))
    line.SetLayer(pcbnew.F_SilkS)
    board.Add(line)

# Power section
add_label("POWER", 135, 63)
add_box(130, 65, 160, 85)

# Input section
add_label("BALANCED INPUT", 175, 80)
add_box(165, 82, 192, 115)

# Scaling section
add_label("SCALING", 145, 103)
add_box(135, 105, 160, 125)

# Output section
add_label("LINE DRIVER", 145, 30)
add_box(115, 32, 165, 58)

# Digital section
add_label("DIGITAL PROCESSING", 80, 60)
add_box(65, 62, 110, 105)

# Clear old tracks so we don't have spaghetti
for t in list(board.GetTracks()):
    board.Remove(t)
for z in list(board.Zones()):
    board.Remove(z)

pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
print("Perfect placement saved.")
