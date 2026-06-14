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

def move_block_absolute_center(refs, target_cx, target_cy):
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    
    fps = []
    for fp in board.GetFootprints():
        if get_ref(fp) in refs:
            fps.append(fp)
            pos = fp.GetPosition()
            min_x = min(min_x, pos.x)
            min_y = min(min_y, pos.y)
            max_x = max(max_x, pos.x)
            max_y = max(max_y, pos.y)
            
    if min_x == float('inf'): return
    
    current_cx = (min_x + max_x) // 2
    current_cy = (min_y + max_y) // 2
    
    dx = mm(target_cx) - current_cx
    dy = mm(target_cy) - current_cy
    
    for fp in fps:
        pos = fp.GetPosition()
        fp.SetPosition(pcbnew.VECTOR2I(pos.x + dx, pos.y + dy))

# U3 (Scaling) Block - Move to Center-Top
u3_refs = ['U3', 'C15', 'C16', 'C17', 'C18', 'R3', 'R4', 'R5', 'R6']
move_block_absolute_center(u3_refs, target_cx=140, target_cy=85) # slightly left to avoid input stage

# Power Block - Move down
power_refs = ['U1', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'D1', 'D2']
move_block_absolute_center(power_refs, target_cx=140, target_cy=140)

# Daisy Seed - Move down
daisy_refs = ['U5', 'U6', 'U7']
move_block_absolute_center(daisy_refs, target_cx=70, target_cy=135)

pcbnew.SaveBoard(board_path, board)
print("Blocks properly rearranged.")
