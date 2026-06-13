"""
Fix courtyard overlaps, remove J1 vias, and re-route with 2-layer strategy.
"""
import pcbnew
import math

BOARD_IN = 'build/icio500/icio500.kicad_pcb'

def add_track(board, start, end, layer, net, width=0.25):
    if start is None or end is None:
        return
    if abs(start[0]-end[0]) < 0.001 and abs(start[1]-end[1]) < 0.001:
        return
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

def pad_pos(board, ref, pad_num):
    fp = board.FindFootprintByReference(ref)
    if fp is None:
        return None
    pad = fp.FindPadByNumber(str(pad_num))
    if pad is None:
        return None
    pos = pad.GetPosition()
    return (pos.x / 1e6, pos.y / 1e6)

def pad_net(board, ref, pad_num):
    fp = board.FindFootprintByReference(ref)
    if fp is None:
        return 0
    pad = fp.FindPadByNumber(str(pad_num))
    if pad is None:
        return 0
    return pad.GetNetCode()

def place(board, ref, x, y, rot=None):
    fp = board.FindFootprintByReference(ref)
    if fp is None:
        return
    fp.SetPosition(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)))
    if rot is not None:
        fp.SetOrientationDegrees(rot)

def build_mst(points):
    if len(points) <= 1:
        return []
    n = len(points)
    in_tree = [False] * n
    in_tree[0] = True
    edges = []
    for _ in range(n - 1):
        best_d = float('inf')
        best_i, best_j = -1, -1
        for i in range(n):
            if not in_tree[i]:
                continue
            for j in range(n):
                if in_tree[j]:
                    continue
                d = dist(points[i], points[j])
                if d < best_d:
                    best_d = d
                    best_i, best_j = i, j
        if best_j >= 0:
            in_tree[best_j] = True
            edges.append((best_i, best_j))
    return edges

def main():
    board = pcbnew.LoadBoard(BOARD_IN)
    FCu = pcbnew.F_Cu
    BCu = pcbnew.B_Cu
    
    # =====================================================
    # STEP 1: Fix courtyard overlaps - spread diodes out
    # =====================================================
    # D3-D6 are at (172, 93/97/103/107) with 4mm spacing - need 5mm
    place(board, "D3", 177, 92, 90)   # In+ -> V+  (moved right and up)
    place(board, "D4", 177, 98, 90)   # V- -> In+
    place(board, "D5", 177, 103, 90)  # In- -> V+
    place(board, "D6", 177, 109, 90)  # V- -> In-
    
    # =====================================================
    # STEP 2: Remove ALL existing tracks and vias
    # =====================================================
    to_remove = list(board.GetTracks())
    for t in to_remove:
        board.Remove(t)
    print(f"Removed {len(to_remove)} tracks/vias")
    
    # =====================================================
    # STEP 3: Smart 2-layer routing using MST
    # =====================================================
    
    # Build net -> pad positions map
    net_pads = {}
    for fp in board.Footprints():
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
    
    power_nets = {'v_plus', 'v_minus', 'gnd', 'v_plus_16v', 'v_minus_16v',
                  'daisy_5v_power', 'daisy_digital_gnd', 'chassis_gnd'}
    
    # Assign layers to nets to avoid crossings
    # Strategy: Route horizontal-dominant nets on F.Cu, vertical-dominant on B.Cu
    # Or simply: alternate layers per net to spread the load
    
    net_list = sorted(net_pads.items(), key=lambda x: len(x[1]['pads']), reverse=True)
    
    total_routed = 0
    
    for idx, (net_code, info) in enumerate(net_list):
        name = info['name']
        pads = info['pads']
        
        if len(pads) < 2:
            continue
        
        # Deduplicate very close pads
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
            continue
        
        edges = build_mst(unique_pads)
        width = 0.4 if name in power_nets else 0.25
        
        # Alternate layers: even nets on F.Cu, odd nets on B.Cu
        # But power nets always start on F.Cu
        if name in power_nets:
            layer = FCu
        else:
            layer = FCu if idx % 2 == 0 else BCu
        
        for i, j in edges:
            p1 = unique_pads[i]
            p2 = unique_pads[j]
            
            # For B.Cu routes, add vias at both ends
            if layer == BCu:
                add_via(board, p1, net_code)
                add_via(board, p2, net_code)
            
            # Route with L-shape
            mid = (p2[0], p1[1])
            add_track(board, p1, mid, layer, net_code, width)
            add_track(board, mid, p2, layer, net_code, width)
            total_routed += 1
    
    print(f"Routed {total_routed} connections")
    
    pcbnew.SaveBoard(BOARD_IN, board)
    print("Done.")

if __name__ == '__main__':
    main()
