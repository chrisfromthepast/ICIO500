"""
Smart autorouter: For each net, find ALL pads, build a minimal spanning tree,
and route the edges. Uses F.Cu primarily with B.Cu for crossings.
"""
import pcbnew
import math

BOARD_IN = 'build/icio500/icio500.kicad_pcb'

def add_track(board, start, end, layer, net, width=0.25):
    if start is None or end is None:
        return
    if abs(start[0]-end[0]) < 0.001 and abs(start[1]-end[1]) < 0.001:
        return  # zero-length track
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(pcbnew.VECTOR2I(int(start[0]*1e6), int(start[1]*1e6)))
    track.SetEnd(pcbnew.VECTOR2I(int(end[0]*1e6), int(end[1]*1e6)))
    track.SetWidth(pcbnew.FromMM(width))
    track.SetLayer(layer)
    track.SetNetCode(net)
    board.Add(track)

def add_via(board, pos, net):
    if pos is None:
        return
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I(int(pos[0]*1e6), int(pos[1]*1e6)))
    via.SetWidth(pcbnew.FromMM(0.6))
    via.SetDrill(pcbnew.FromMM(0.3))
    via.SetNetCode(net)
    board.Add(via)

def dist(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def route_manhattan(board, p1, p2, layer, net, width=0.25):
    """L-shaped Manhattan route"""
    if p1 is None or p2 is None:
        return
    # Choose the shorter intermediate
    mid = (p2[0], p1[1])
    add_track(board, p1, mid, layer, net, width)
    add_track(board, mid, p2, layer, net, width)

def build_mst(points):
    """Prim's algorithm for minimum spanning tree. Returns list of (i, j) edges."""
    if len(points) <= 1:
        return []
    
    n = len(points)
    in_tree = [False] * n
    in_tree[0] = True
    edges = []
    
    for _ in range(n - 1):
        best_dist = float('inf')
        best_i = -1
        best_j = -1
        for i in range(n):
            if not in_tree[i]:
                continue
            for j in range(n):
                if in_tree[j]:
                    continue
                d = dist(points[i], points[j])
                if d < best_dist:
                    best_dist = d
                    best_i = i
                    best_j = j
        if best_j >= 0:
            in_tree[best_j] = True
            edges.append((best_i, best_j))
    
    return edges

def main():
    board = pcbnew.LoadBoard(BOARD_IN)
    FCu = pcbnew.F_Cu
    BCu = pcbnew.B_Cu
    
    # Build net -> pad positions map
    net_pads = {}  # net_code -> [(x, y), ...]
    
    for fp in board.Footprints():
        ref = fp.GetReference()
        for pad in fp.Pads():
            net_code = pad.GetNetCode()
            net_name = pad.GetNetname()
            if net_code == 0 or not net_name:
                continue
            pos = pad.GetPosition()
            x, y = pos.x / 1e6, pos.y / 1e6
            
            if net_code not in net_pads:
                net_pads[net_code] = {'name': net_name, 'pads': []}
            net_pads[net_code]['pads'].append((x, y))
    
    # Power net widths
    power_nets = {'v_plus', 'v_minus', 'gnd', 'v_plus_16v', 'v_minus_16v', 
                  'daisy_5v_power', 'daisy_digital_gnd', 'chassis_gnd'}
    
    total_routed = 0
    total_nets = 0
    
    for net_code, info in sorted(net_pads.items()):
        name = info['name']
        pads = info['pads']
        
        if len(pads) < 2:
            continue
        
        total_nets += 1
        
        # Deduplicate very close pads (same physical pad on multiple layers)
        unique_pads = []
        for p in pads:
            is_dup = False
            for u in unique_pads:
                if dist(p, u) < 0.05:
                    is_dup = True
                    break
            if not is_dup:
                unique_pads.append(p)
        
        if len(unique_pads) < 2:
            # All pads at same position (multi-layer through-hole) — add via
            add_via(board, pads[0], net_code)
            total_routed += 1
            continue
        
        # Build MST
        edges = build_mst(unique_pads)
        
        width = 0.4 if name in power_nets else 0.25
        
        for i, j in edges:
            p1 = unique_pads[i]
            p2 = unique_pads[j]
            route_manhattan(board, p1, p2, FCu, net_code, width)
            total_routed += 1
        
        # For through-hole pads (J1, U1, U5, U6, U7), add vias at pad positions
        # to ensure connectivity on both layers
    
    print(f"Routed {total_routed} connections across {total_nets} nets")
    
    # Add silkscreen labels in empty space
    def add_label(text, x, y, size=1.0, thickness=0.15):
        txt = pcbnew.PCB_TEXT(board)
        txt.SetText(text)
        txt.SetPosition(pcbnew.VECTOR2I(int(x*1e6), int(y*1e6)))
        txt.SetTextSize(pcbnew.VECTOR2I(int(size*1e6), int(size*1e6)))
        txt.SetTextThickness(int(thickness*1e6))
        txt.SetLayer(pcbnew.F_SilkS)
        board.Add(txt)
    
    add_label("POWER", 170, 117, 1.0)
    add_label("INPUT", 160, 113, 1.0)
    add_label("SCALING", 140, 83, 1.0)
    add_label("DRIVER", 133, 58, 1.0)
    add_label("DAISY SEED", 75, 80, 1.0)
    
    pcbnew.SaveBoard(BOARD_IN, board)
    print("Done.")

if __name__ == '__main__':
    main()
