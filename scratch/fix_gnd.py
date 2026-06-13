import pcbnew
import math

board_path = 'build/icio500/icio500.kicad_pcb'
board = pcbnew.LoadBoard(board_path)

def add_track(board, start, end, layer, net, width=0.25):
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(pcbnew.VECTOR2I(int(start[0]*1e6), int(start[1]*1e6)))
    track.SetEnd(pcbnew.VECTOR2I(int(end[0]*1e6), int(end[1]*1e6)))
    track.SetWidth(pcbnew.FromMM(width))
    track.SetLayer(layer)
    track.SetNetCode(net)
    board.Add(track)

c26 = board.FindFootprintByReference("C26")
c26_p2 = c26.FindPadByNumber("2")
net_gnd = c26_p2.GetNetCode()
c26_p2_pos = (c26_p2.GetPosition().x/1e6, c26_p2.GetPosition().y/1e6)

# Find all GND pads to find the nearest one
gnd_pads = []
for fp in board.Footprints():
    for pad in fp.Pads():
        if pad.GetNetCode() == net_gnd:
            pos = pad.GetPosition()
            gnd_pads.append((pos.x/1e6, pos.y/1e6))

def get_nearest(pos, candidates):
    best_dist = 999999
    best_c = None
    for c in candidates:
        if abs(c[0] - pos[0]) < 0.1 and abs(c[1] - pos[1]) < 0.1:
            continue
        dist = math.hypot(c[0]-pos[0], c[1]-pos[1])
        if dist < best_dist:
            best_dist = dist
            best_c = c
    return best_c

nearest_to_c26 = get_nearest(c26_p2_pos, gnd_pads)
print(f"Nearest to C26 pad 2 {c26_p2_pos}: {nearest_to_c26}")

# Route C26 pad 2 directly to nearest GND pad on B.Cu
v1 = (c26_p2_pos[0], c26_p2_pos[1] - 1.5)
# via already exists from final_route.py
add_track(board, v1, nearest_to_c26, pcbnew.B_Cu, net_gnd)

track_pos = (174.3026, 92.2250)
nearest_to_track = get_nearest(track_pos, gnd_pads)
print(f"Nearest to track {track_pos}: {nearest_to_track}")
# via already exists from final_route.py
add_track(board, track_pos, nearest_to_track, pcbnew.B_Cu, net_gnd)

pcbnew.SaveBoard(board_path, board)
print("Saved GND fix.")
