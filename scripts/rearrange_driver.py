import pcbnew
import os

def mm(v): return int(v * 1_000_000)

board_path = 'build/icio500/icio500.kicad_pcb'
board = pcbnew.LoadBoard(board_path)

def get_ref(fp):
    try:
        if hasattr(fp, 'GetReference'):
            return fp.GetReference()
    except:
        pass
    return ""

driver_refs = ['U4', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26', 'R9', 'R10', 'D7', 'D8', 'D9', 'D10']

# Find current center of U4
u4_fp = None
for fp in board.GetFootprints():
    if get_ref(fp) == 'U4':
        u4_fp = fp
        break

if not u4_fp:
    print("U4 not found!")
    exit(1)

pos = u4_fp.GetPosition()
cx = pos.x
cy = pos.y

def set_pos(ref, dx_mm, dy_mm, rot_deg=0):
    for fp in board.GetFootprints():
        if get_ref(fp) == ref:
            fp.SetPosition(pcbnew.VECTOR2I(cx + mm(dx_mm), cy + mm(dy_mm)))
            fp.SetOrientation(pcbnew.EDA_ANGLE(rot_deg, pcbnew.DEGREES_T))
            break

# Layout design for THAT1646 (U4)
# U4 is SOIC-8. Pins: 1=Out-, 2=OutSense-, 3=GND, 4=V-, 5=In, 6=OutSense+, 7=V+, 8=Out+
# Pin 1 is Top-Left, Pin 8 is Top-Right.

# 1. Local Bypass Caps (C21 for V-, C22 for V+)
# Place C21 (V-) near Pin 4 (bottom left). 
set_pos('C21', -3, 6, 90)
# Place C22 (V+) near Pin 7 (bottom right).
set_pos('C22', 3, 6, 90)

# 2. Bulk Bypass Caps (C23 for V-, C24 for V+)
set_pos('C23', -8, 6, 90)
set_pos('C24', 8, 6, 90)

# 3. Zobel Networks (R9/C25 for Out+, R10/C26 for Out-)
# R9 and C25
set_pos('R9', 12, -4, 0)
set_pos('C25', 16, -4, 0)

# R10 and C26
set_pos('R10', 12, 4, 0)
set_pos('C26', 16, 4, 0)

# 4. Protection Diodes (D7, D8 for Out+, D9, D10 for Out-)
# Stack them neatly on the far right
set_pos('D7', 22, -6, 90)
set_pos('D8', 22, -2, 90)
set_pos('D9', 22, 2, 90)
set_pos('D10', 22, 6, 90)

pcbnew.SaveBoard(board_path, board)
print("LINE DRIVER layout completed successfully.")
