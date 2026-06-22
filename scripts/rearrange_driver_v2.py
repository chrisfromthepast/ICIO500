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

# U4 is SOIC-8. Center is at (0,0) relative to itself.
# Let's mimic the user's BALANCED INPUT style exactly.

# 1. Electrolytic Caps (C23, C24) on the LEFT, stacked vertically.
# Spacing them nicely.
set_pos('C23', -12, -4, 0)
set_pos('C24', -12,  4, 0)

# 2. Local Bypass Caps (C21, C22) ABOVE and BELOW the IC (U4).
set_pos('C21', 0, -5.5, 0)
set_pos('C22', 0,  5.5, 0)

# 3. Zobel Networks (R9/C25, R10/C26) on the RIGHT side.
# Let's put R9, C25 next to each other on the top half.
set_pos('R9',   8, -3, 90)
set_pos('C25', 11, -3, 90)

# Let's put R10, C26 next to each other on the bottom half.
set_pos('R10',  8,  3, 90)
set_pos('C26', 11,  3, 90)

# 4. Protection Diodes (D7-D10) in a 2x2 grid on the FAR RIGHT.
# Mimicking D3-D6 from the Balanced Input box.
set_pos('D7',  17, -3, 0)
set_pos('D8',  17,  3, 0)
set_pos('D9',  21, -3, 0)
set_pos('D10', 21,  3, 0)

pcbnew.SaveBoard(board_path, board)
print("LINE DRIVER layout improved.")
