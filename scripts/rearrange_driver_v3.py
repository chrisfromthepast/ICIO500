import pcbnew

def mm(v): return int(v * 1_000_000)

board_path = 'build/icio500/icio500.kicad_pcb'
board = pcbnew.LoadBoard(board_path)

def get_ref(fp):
    try:
        if hasattr(fp, 'GetReference'): return fp.GetReference()
    except: pass
    return ""

u4_fp = None
for fp in board.GetFootprints():
    if get_ref(fp) == 'U4':
        u4_fp = fp
        break

pos = u4_fp.GetPosition()
cx = pos.x
cy = pos.y

def set_pos(ref, dx_mm, dy_mm, rot_deg=0):
    for fp in board.GetFootprints():
        if get_ref(fp) == ref:
            fp.SetPosition(pcbnew.VECTOR2I(cx + mm(dx_mm), cy + mm(dy_mm)))
            fp.SetOrientation(pcbnew.EDA_ANGLE(rot_deg, pcbnew.DEGREES_T))
            break

# 1. Electrolytic Caps (C23, C24) on the LEFT, nicely spaced.
set_pos('C23', -18, -8, 0)
set_pos('C24', -18,  8, 0)

# 2. Local Bypass Caps (C21, C22) ABOVE and BELOW the IC (U4).
# 0 degree means horizontal. Let's put them at Y= -8 and +8.
set_pos('C21', 0, -8, 0)
set_pos('C22', 0,  8, 0)

# 3. Zobel Networks (R9/C25, R10/C26) on the RIGHT side.
# Rotate them 90 degrees so they stack nicely horizontally.
set_pos('R9',  10, -5, 90)
set_pos('C25', 14, -5, 90)

set_pos('R10', 10,  5, 90)
set_pos('C26', 14,  5, 90)

# 4. Protection Diodes (D7-D10) in a 2x2 grid on the FAR RIGHT.
# Spread them out!
set_pos('D7',  22, -6, 0)
set_pos('D9',  28, -6, 0)

set_pos('D8',  22,  6, 0)
set_pos('D10', 28,  6, 0)

# Move R7 and R8 out of the way! They belong to scaling.
# We will just bump them down 20mm so they don't sit in the Line Driver box.
for fp in board.GetFootprints():
    ref = get_ref(fp)
    if ref in ['R7', 'R8']:
        fp.SetPosition(pcbnew.VECTOR2I(fp.GetPosition().x, fp.GetPosition().y + mm(20)))

pcbnew.SaveBoard(board_path, board)
print("LINE DRIVER layout perfected.")
