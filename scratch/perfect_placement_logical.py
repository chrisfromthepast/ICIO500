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
# 1. POWER SUPPLY (Center, isolates Analog from Digital)
# ==========================================================
place("U1", 145, 105, 0)     # DC-DC Converter
place("C1", 135, 100, 0)     # Bulk +
place("C3", 135, 110, 0)     # Bulk -
place("C2", 140, 100, 0)     # Cer +
place("C4", 140, 110, 0)     # Cer -
place("C5", 155, 100, 0)     # Iso +
place("C6", 155, 110, 0)     # Iso cer
place("D1", 185, 140, 0)     # Protection Diode near J1
place("D2", 185, 150, 0)     # Protection Diode near J1

# ==========================================================
# 2. BALANCED INPUT (Right side, near Edge Connector)
# ==========================================================
place("U2", 175, 105, 0)     # Input receiver
place("R1", 185, 100, 0)     
place("R2", 185, 110, 0)
place("C12", 180, 100, 0)    
place("C13", 180, 110, 0)
place("C14", 170, 105, 90)   
place("C9",  183, 105, 90)   
place("C10", 188, 98, 0)     
place("C11", 188, 112, 0)
place("D3", 170, 95, 0)
place("D4", 175, 95, 0)
place("D5", 170, 115, 0)
place("D6", 175, 115, 0)
place("C7", 175, 99, 90)
place("C15", 172, 99, 90)
place("C8", 175, 111, 90)
place("C16", 172, 111, 90)

# ==========================================================
# 3. SCALING & SHIFTING (Right side, below Input)
# ==========================================================
place("U3", 165, 140, 0)
place("R3", 173, 135, 0)
place("R4", 173, 138, 0)
place("R5", 173, 142, 0)
place("R6", 173, 145, 0)
place("C17", 160, 135, 90)
place("C18", 160, 145, 90)

# ==========================================================
# 4. LINE DRIVER (Right side, above Input)
# ==========================================================
place("U4", 165, 70, 0)
place("C19", 173, 67, 90)
place("C20", 176, 67, 90)
place("C21", 173, 73, 90)
place("C22", 176, 73, 90)
place("C23", 158, 63, 0)
place("C24", 158, 77, 0)
place("R7", 150, 63, 0)
place("C25", 143, 63, 0)
place("R8", 150, 77, 0)
place("C26", 143, 77, 0)

# ==========================================================
# 5. DIGITAL PROCESSING (Far Left, isolated)
# ==========================================================
place("U5", 70, 105, 90)     # Daisy Seed
place("U6", 90, 130, 0)
place("U7", 110, 130, 0)

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
add_label("POWER", 145, 87)
add_box(130, 85, 160, 115)

# Input section
add_label("BALANCED INPUT", 175, 87)
add_box(166, 85, 195, 125)

# Scaling section
add_label("SCALING", 165, 128)
add_box(155, 126, 185, 155)

# Output section
add_label("LINE DRIVER", 165, 55)
add_box(135, 57, 185, 83)

# Digital section
add_label("DIGITAL PROCESSING", 95, 80)
add_box(60, 82, 128, 145)

pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
print("Logical placement saved.")
