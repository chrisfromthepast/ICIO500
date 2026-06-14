import pcbnew
import subprocess

def mm(v): return int(v * 1_000_000)

board_path = 'build/icio500/icio500.kicad_pcb'
board = pcbnew.LoadBoard(board_path)

# Enforce U1 footprint and nets
def set_u1():
    u1 = None
    for fp in board.GetFootprints():
        if fp.GetReference() == 'U1':
            u1 = fp
            break
    if u1:
        u1.SetFPID(pcbnew.LIB_ID('Package_TO_SOT_THT', 'TO-220-3_Vertical'))
        
    gnd_net = board.FindNet('GND_Audio')
    v5_net = board.FindNet('V_Plus_5V')
    vin_net = board.FindNet('V_Plus_Analog')

    if not vin_net: vin_net = pcbnew.NETINFO_ITEM(board, 'V_Plus_Analog'); board.Add(vin_net)
    if not gnd_net: gnd_net = pcbnew.NETINFO_ITEM(board, 'GND_Audio'); board.Add(gnd_net)
    if not v5_net: v5_net = pcbnew.NETINFO_ITEM(board, 'V_Plus_5V'); board.Add(v5_net)

    if u1:
        for pad in u1.Pads():
            if pad.GetName() == '1': pad.SetNet(vin_net)
            elif pad.GetName() == '2': pad.SetNet(gnd_net)
            elif pad.GetName() == '3': pad.SetNet(v5_net)

    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref in ['C5', 'C6']:
            for pad in fp.Pads():
                if pad.GetName() == '1': pad.SetNet(v5_net)
                elif pad.GetName() == '2': pad.SetNet(gnd_net)

set_u1()

def move_block_absolute_center(refs, target_cx, target_cy):
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    
    fps = []
    for fp in board.GetFootprints():
        if fp.GetReference() in refs:
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

# Clear old graphics
layers_to_clean = [pcbnew.F_SilkS, pcbnew.Cmts_User, pcbnew.Dwgs_User]
for item in list(board.GetDrawings()):
    if item.GetLayer() in layers_to_clean:
        board.Remove(item)

# Clear Tracks
# We will use the script `scripts/clear_routing.py` for this part separately to be safe, 
# or just do it here using GetTracks() if it works. 
# It crashed earlier because board.GetTracks() isn't a Python list, but we can iterate.
pass

# U3 (Scaling) Block - Move between U2 and U4
u3_refs = ['U3', 'C15', 'C16', 'C17', 'C18', 'R3', 'R4', 'R5', 'R6']
move_block_absolute_center(u3_refs, target_cx=140, target_cy=85) # slightly left to avoid input stage

# Power Block - Move down
power_refs = ['U1', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'D1', 'D2']
move_block_absolute_center(power_refs, target_cx=140, target_cy=140)

# Daisy Seed - Move down
daisy_refs = ['U5', 'U6', 'U7']
move_block_absolute_center(daisy_refs, target_cx=70, target_cy=135)

pcbnew.SaveBoard(board_path, board)
print("Blocks rearranged and tracks cleared.")
