import pcbnew

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

# Collect all footprints first to avoid SWIG iterator crashes
fps = {fp.GetReference(): fp for fp in board.GetFootprints()}

def place(ref, x, y, rot=0):
    if ref in fps:
        fp = fps[ref]
        fp.SetPosition(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)))
        fp.SetOrientationDegrees(rot)

to_delete = []
for dwg in list(board.Drawings()):
    if dwg.GetLayer() == pcbnew.F_SilkS:
        if isinstance(dwg, pcbnew.PCB_TEXT) or isinstance(dwg, pcbnew.PCB_SHAPE):
            to_delete.append(dwg)
for t in list(board.GetTracks()):
    to_delete.append(t)
for z in list(board.Zones()):
    to_delete.append(z)
for item in to_delete:
    try: board.Remove(item)
    except: pass

# ==========================================================
# 1. POWER SUPPLY (Middle Right Column: X=140-168, Y=58-155)
# ==========================================================
place("U1", 154, 105, 0)     # DC-DC Converter
place("C1", 145, 100, 0)     # Bulk +
place("C3", 145, 110, 0)     # Bulk -
place("C2", 149, 100, 0)     # Cer +
place("C4", 149, 110, 0)     # Cer -
place("C5", 163, 100, 0)     # Iso +
place("C6", 163, 110, 0)     # Iso cer
place("D1", 163, 130, 0)     # Protection Diode
place("D2", 163, 140, 0)     # Protection Diode

# ==========================================================
# 2. BALANCED INPUT (Far Right Column: X=168-192, Y=58-155)
# ==========================================================
place("U2", 180, 105, 0)     # Input receiver
place("R1", 187, 100, 0)     
place("R2", 187, 110, 0)
place("C12", 183, 100, 0)    
place("C13", 183, 110, 0)
place("C14", 175, 105, 90)   
place("C9",  183, 105, 90)   
place("C10", 187, 92, 0)     
place("C11", 187, 118, 0)
place("D3", 175, 95, 0)
place("D4", 180, 95, 0)
place("D5", 175, 115, 0)
place("D6", 180, 115, 0)
place("C7", 180, 99, 90)
place("C15", 177, 99, 90)
place("C8", 180, 111, 90)
place("C16", 177, 111, 90)

# ==========================================================
# 3. SCALING & SHIFTING (Bottom Left Row: X=55-140, Y=125-155)
# ==========================================================
place("U3", 100, 140, 0)
place("R3", 108, 135, 0)
place("R4", 108, 138, 0)
place("R5", 108, 142, 0)
place("R6", 108, 145, 0)
place("C17", 95, 135, 90)
place("C18", 95, 145, 90)

# ==========================================================
# 4. LINE DRIVER (Top Left Row: X=55-140, Y=58-82)
# ==========================================================
place("U4", 100, 70, 0)
place("C19", 108, 67, 90)
place("C20", 111, 67, 90)
place("C21", 108, 73, 90)
place("C22", 111, 73, 90)
place("C23", 93, 63, 0)
place("C24", 93, 77, 0)
place("R7", 85, 63, 0)
place("C25", 78, 63, 0)
place("R8", 85, 77, 0)
place("C26", 78, 77, 0)

# ==========================================================
# 5. DIGITAL PROCESSING (Middle Left Row: X=55-140, Y=82-125)
# ==========================================================
place("U5", 65, 105, 90)     # Daisy Seed
place("U6", 130, 95, 0)
place("U7", 130, 115, 0)

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
add_label("POWER", 154, 63)
add_box(140, 58, 168, 155)

# Input section
add_label("BALANCED INPUT", 180, 63)
add_box(168, 58, 196, 155)

# Scaling section
add_label("SCALING", 100, 150)
add_box(55, 125, 140, 155)

# Output section
add_label("LINE DRIVER", 100, 62)
add_box(55, 58, 140, 82)

# Digital section
add_label("DIGITAL PROCESSING", 100, 86)
add_box(55, 82, 140, 125)

pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
print("Perfect placement saved.")
