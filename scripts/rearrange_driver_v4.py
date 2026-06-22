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

def set_pos(ref, dx_mm, dy_mm, rot_deg=0, ref_dx=0, ref_dy=0):
    for fp in board.GetFootprints():
        if get_ref(fp) == ref:
            # Move footprint
            new_x = cx + mm(dx_mm)
            new_y = cy + mm(dy_mm)
            fp.SetPosition(pcbnew.VECTOR2I(new_x, new_y))
            fp.SetOrientation(pcbnew.EDA_ANGLE(rot_deg, pcbnew.DEGREES_T))
            
            # Move reference text
            ref_item = fp.Reference()
            ref_item.SetPosition(pcbnew.VECTOR2I(new_x + mm(ref_dx), new_y + mm(ref_dy)))
            ref_item.SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T)) # Keep text horizontal
            ref_item.SetKeepUpright(True)
            break

# 1. Electrolytic Caps on the left
set_pos('C23', -15, -6, rot_deg=0, ref_dx=0, ref_dy=-4.5) # Text above
set_pos('C24', -15,  6, rot_deg=0, ref_dx=0, ref_dy=-4.5) # Text above

# 2. Local Bypass Caps directly above/below U4
set_pos('C21', 0, -6, rot_deg=0, ref_dx=0, ref_dy=-2.5) # Text above
set_pos('C22', 0,  6, rot_deg=0, ref_dx=0, ref_dy=2.5)  # Text below

# U4 reference text
u4_ref = u4_fp.Reference()
u4_ref.SetPosition(pcbnew.VECTOR2I(cx, cy + mm(3.5))) # Text below U4
u4_ref.SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))

# 3. Diodes to the right of U4
set_pos('D7',  10, -2.5, rot_deg=0, ref_dx=0, ref_dy=-2) # Text above
set_pos('D9',  15, -2.5, rot_deg=0, ref_dx=0, ref_dy=-2) # Text above

set_pos('D8',  10,  2.5, rot_deg=0, ref_dx=0, ref_dy=2)  # Text below
set_pos('D10', 15,  2.5, rot_deg=0, ref_dx=0, ref_dy=2)  # Text below

# 4. Zobel Networks on the far right
set_pos('R9',  21, -2.5, rot_deg=0, ref_dx=0, ref_dy=-2) # Text above
set_pos('C25', 26, -2.5, rot_deg=0, ref_dx=0, ref_dy=-2) # Text above

set_pos('R10', 21,  2.5, rot_deg=0, ref_dx=0, ref_dy=2)  # Text below
set_pos('C26', 26,  2.5, rot_deg=0, ref_dx=0, ref_dy=2)  # Text below

pcbnew.SaveBoard(board_path, board)
print("LINE DRIVER layout absolutely perfected.")
