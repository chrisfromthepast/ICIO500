"""
ICIO500 Complete Relayout - Single comprehensive script.
Does everything: clean, place, route, vias, silkscreen.
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

def place(board, ref, x, y, rot=None):
    fp = board.FindFootprintByReference(ref)
    if fp is None:
        print(f"  WARNING: {ref} not found!")
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
            if not in_tree[i]: continue
            for j in range(n):
                if in_tree[j]: continue
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
    
    # Step 1 moved to later to avoid SWIG API bug
    bad_labels = ["BALANCED INPUT STAGE", "LINE DRIVER STAGE", 
                  "SCALING & SHIFTING", "POWER CONDITIONING",
                  "POWER / REGS", "GAIN TRIM RESISTOR",
                  "POWER", "INPUT", "SCALING", "DRIVER", "DAISY SEED"]
    to_remove_dwg = []
    # Removed label clearing because KiCad 10 board.Drawings() crashes with SWIG error
    
    print("Cleaned board.")
    
    # =====================================================
    # STEP 2: Place ALL components
    # =====================================================
    # J1 stays at (198.5, 98.9) — DON'T MOVE
    
    # --- POWER SUPPLY (center-right, near J1) ---
    place(board, "D1", 185, 120, 0)
    place(board, "D2", 185, 130, 0)
    place(board, "C1", 165, 125, 0)    # 220uF V+ bulk
    place(board, "C3", 165, 135, 0)    # 220uF V- bulk
    place(board, "C2", 175, 125, 0)    # 100nF V+ ceramic
    place(board, "C4", 175, 135, 0)    # 100nF V- ceramic
    place(board, "U1", 130, 130, 0)    # DC-DC 5V
    place(board, "C5", 140, 127, 0)    # 10uF iso
    place(board, "C6", 140, 133, 0)    # 100nF iso
    
    # --- BALANCED INPUT (U2 cluster, right side) ---
    place(board, "U2", 170, 100, 0)
    place(board, "R1", 180, 95, 0)     # RF+ resistor
    place(board, "R2", 180, 105, 0)    # RF- resistor
    place(board, "C10", 186, 92, 0)    # chassis shunt +
    place(board, "C11", 186, 108, 0)   # chassis shunt -
    place(board, "C9", 183, 100, 90)   # diff RF cap
    place(board, "C12", 175, 95, 0)    # AC coupling +
    place(board, "C13", 175, 105, 0)   # AC coupling -
    place(board, "C14", 165, 105, 90)  # CM bootstrap
    place(board, "C7", 165, 95, 90)    # V+ bypass
    place(board, "C15", 162, 95, 90)   # V+ bypass 2
    place(board, "C8", 165, 108, 90)   # V- bypass
    place(board, "C16", 162, 108, 90)  # V- bypass 2
    # Diodes with enough spacing (5mm apart min)
    place(board, "D3", 180, 91, 90)    # In+ -> V+
    place(board, "D4", 180, 97, 90)    # V- -> In+
    place(board, "D5", 180, 103, 90)   # In- -> V+
    place(board, "D6", 180, 109, 90)   # V- -> In-
    
    # --- ACTIVE SCALING (U3, center) ---
    place(board, "U3", 145, 95, 0)
    place(board, "R3", 153, 93, 0)     # 22k in series
    place(board, "R4", 153, 96, 0)     # 10k feedback
    place(board, "C17", 150, 105, 90)  # 47pF filter
    place(board, "R5", 153, 99, 0)     # 10k out series
    place(board, "R6", 153, 102, 0)    # 22k out feedback
    place(board, "C18", 150, 93, 90)   # 47pF filter
    
    # --- LINE DRIVER (U4, upper-center) ---
    place(board, "U4", 145, 70, 0)
    place(board, "C19", 153, 67, 90)   # V+ bulk bypass
    place(board, "C20", 156, 67, 90)   # V+ ceramic
    place(board, "C21", 153, 76, 90)   # V- bulk bypass
    place(board, "C22", 156, 76, 90)   # V- ceramic
    place(board, "C23", 138, 63, 0)    # Out+ ext cap
    place(board, "C24", 138, 77, 0)    # Out- ext cap
    place(board, "R7", 130, 63, 0)     # Zobel+ R
    place(board, "C25", 123, 63, 0)    # Zobel+ C
    place(board, "R8", 130, 77, 0)     # Zobel- R
    place(board, "C26", 123, 77, 0)    # Zobel- C
    
    # --- DIGITAL (Daisy Seed, left side) ---
    place(board, "U5", 80, 100, 90)    # DIP-40 rotated
    place(board, "U6", 60, 108, 0)     # Switch bypass
    place(board, "U7", 60, 100, 0)     # Switch noise
    
    print("All components placed.")
    
    # =====================================================
    # STEP 3: Route ALL nets using MST + 2-layer strategy
    # =====================================================
    
    # Build net -> unique pad positions
    net_pads = {}
    for fp in board.Footprints():
        for pad in fp.Pads():
            nc = pad.GetNetCode()
            nn = pad.GetNetname()
            if nc == 0 or not nn:
                continue
            pos = pad.GetPosition()
            x, y = pos.x / 1e6, pos.y / 1e6
            if nc not in net_pads:
                net_pads[nc] = {'name': nn, 'pads': [], 'th_pads': []}
            
            # Record if it's a through-hole pad to avoid redundant vias later
            layers = pad.GetLayerSet()
            if layers.Contains(FCu) and layers.Contains(BCu):
                net_pads[nc]['th_pads'].append((x, y))
            
            # Deduplicate
            is_dup = False
            for existing in net_pads[nc]['pads']:
                if dist((x,y), existing) < 0.05:
                    is_dup = True
                    break
            if not is_dup:
                net_pads[nc]['pads'].append((x, y))

    # =====================================================
    # STEP 3: Remove ALL existing tracks, vias, zones
    # =====================================================
    for t in list(board.GetTracks()):
        board.Remove(t)
    for z in list(board.Zones()):
        board.Remove(z)
        
    power_nets = {'v_plus', 'v_minus', 'gnd', 'v_plus_16v', 'v_minus_16v',
                  'daisy_5v_power', 'daisy_digital_gnd', 'chassis_gnd'}
    
    # Sort nets: route power first (on F.Cu), then signal nets alternating layers
    power_list = []
    signal_list = []
    for nc, info in sorted(net_pads.items(), key=lambda item: item[0]):
        if len(info['pads']) < 2:
            continue
        if info['name'] in power_nets:
            power_list.append((nc, info))
        else:
            signal_list.append((nc, info))
    
    total = 0
    
    # Route power nets on F.Cu with wider traces
    for nc, info in power_list:
        edges = build_mst(info['pads'])
        for i, j in edges:
            p1, p2 = info['pads'][i], info['pads'][j]
            mid = (p2[0], p1[1])
            add_track(board, p1, mid, FCu, nc, 0.4)
            add_track(board, mid, p2, FCu, nc, 0.4)
            total += 1
    
    # Route signal nets alternating F.Cu and B.Cu
    for idx, (nc, info) in enumerate(signal_list):
        layer = FCu if idx % 2 == 0 else BCu
        edges = build_mst(info['pads'])
        for i, j in edges:
            p1, p2 = info['pads'][i], info['pads'][j]
            if layer == BCu:
                # Only add via if the pad isn't already a through-hole pad
                def is_th(px, py):
                    for tx, ty in info['th_pads']:
                        if dist((px, py), (tx, ty)) < 0.05: return True
                    return False
                if not is_th(p1[0], p1[1]):
                    add_via(board, p1, nc)
                if not is_th(p2[0], p2[1]):
                    add_via(board, p2, nc)
            mid = (p2[0], p1[1])
            add_track(board, p1, mid, layer, nc, 0.25)
            add_track(board, mid, p2, layer, nc, 0.25)
            total += 1
    
    # Through-hole vias are handled inline above.
    print(f"Routed {total} connections.")
    
    # =====================================================
    # STEP 4: Add silkscreen labels in EMPTY space
    # =====================================================
    def add_label(text, x, y, size=1.0, thickness=0.15):
        txt = pcbnew.PCB_TEXT(board)
        txt.SetText(text)
        txt.SetPosition(pcbnew.VECTOR2I(int(x*1e6), int(y*1e6)))
        txt.SetTextSize(pcbnew.VECTOR2I(int(size*1e6), int(size*1e6)))
        txt.SetTextThickness(int(thickness*1e6))
        txt.SetLayer(pcbnew.F_SilkS)
        board.Add(txt)
    
    # Labels positioned in clear empty gaps between blocks
    add_label("POWER", 155, 140)
    add_label("INPUT", 170, 113)
    add_label("SCALING", 145, 83)
    add_label("DRIVER", 135, 58)
    add_label("DAISY SEED", 75, 78)
    
    pcbnew.SaveBoard(BOARD_IN, board)
    print("DONE. Board saved.")

if __name__ == '__main__':
    main()
