import pcbnew
import os

# Load board
board_path = 'build/icio500/icio500.kicad_pcb'
board = pcbnew.LoadBoard(board_path)

# Helper to move reference text
def move_reference(fp, dx_mm, dy_mm):
    ref = fp.Reference()
    if not ref:
        return
    pos = ref.GetPosition()
    # Convert mm to internal units (nm)
    dx = int(dx_mm * 1e6)
    dy = int(dy_mm * 1e6)
    new_pos = pcbnew.VECTOR2I(pos.x + dx, pos.y + dy)
    ref.SetPosition(new_pos)

# Adjust D4 reference upward by 0.2mm
for fp in board.GetFootprints():
    if fp.GetReference() == 'D4':
        move_reference(fp, 0, 0.2)
        print('Moved D4 reference')

# Adjust D6 reference downward by 0.2mm
for fp in board.GetFootprints():
    if fp.GetReference() == 'D6':
        move_reference(fp, 0, -0.2)
        print('Moved D6 reference')

# Save board
pcbnew.SaveBoard(board_path, board)
print('Silkscreen overlaps adjusted and board saved')
