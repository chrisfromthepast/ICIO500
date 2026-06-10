import pcbnew
import heapq

def mm(val): return int(val * 1000000)
def frm(val): return val / 1000000.0

board_path = 'build/icio500/icio500.kicad_pcb'
board = pcbnew.LoadBoard(board_path)

nets_to_skip = ['', 'gnd', 'chassis_gnd', 'v_plus_16v', 'v_minus_16v', 'v_plus_48v', 'daisy_digital_gnd', 'daisy_5v_power']

print("Extracting pads...")
pads_info = []
for fp in board.GetFootprints():
    for p in fp.Pads():
        netname = str(p.GetNetname())
        if netname and netname not in nets_to_skip:
            pos = pcbnew.VECTOR2I(p.GetPosition())
            pads_info.append({
                'netname': netname,
                'netcode': p.GetNetCode(),
                'x': pos.x,
                'y': pos.y,
                'is_pth': p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH,
                'layer': p.GetLayer()
            })

nets = {}
for info in pads_info:
    nets.setdefault(info['netname'], []).append(info)

rc = board.GetConnectivity()
rc.Build(board)
routed_nets = set([str(t.GetNetname()) for t in board.GetTracks() if t.GetNetname()])
unconnected_nets = [n for n in nets.keys() if n not in routed_nets]

print(f"Routing {len(unconnected_nets)} nets orthogonally on In1_Cu...")

grid = mm(0.5) # 0.5mm grid
W = mm(0.25)

def snap(val):
    return round(val / grid) * grid

obstacles = set() # (x, y)

bbox = board.ComputeBoundingBox()
min_x = snap(bbox.GetX() - mm(10))
max_x = snap(bbox.GetRight() + mm(10))
min_y = snap(bbox.GetY() - mm(10))
max_y = snap(bbox.GetBottom() + mm(10))

for netname in unconnected_nets:
    if netname not in nets: continue
    
    net_pads = nets[netname]
    netcode = net_pads[0]['netcode']
    net_pads.sort(key=lambda p: p['x'])
    
    for i in range(len(net_pads) - 1):
        p1 = net_pads[i]
        p2 = net_pads[i+1]
        
        start_pt = (snap(p1['x']), snap(p1['y']))
        end_pt = (snap(p2['x']), snap(p2['y']))
        
        # A* routing
        open_set = []
        heapq.heappush(open_set, (0, start_pt))
        came_from = {}
        g_score = {start_pt: 0}
        
        def h(p):
            return abs(p[0] - end_pt[0]) + abs(p[1] - end_pt[1])
            
        path = None
        while open_set:
            _, curr = heapq.heappop(open_set)
            
            if curr == end_pt:
                # Reconstruct
                path = [curr]
                while curr in came_from:
                    curr = came_from[curr]
                    path.append(curr)
                path.reverse()
                break
                
            for dx, dy in [(-grid, 0), (grid, 0), (0, -grid), (0, grid)]:
                neighbor = (curr[0] + dx, curr[1] + dy)
                if neighbor[0] < min_x or neighbor[0] > max_x or neighbor[1] < min_y or neighbor[1] > max_y:
                    continue
                if neighbor in obstacles and neighbor != end_pt:
                    continue
                tentative_g = g_score[curr] + grid
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = curr
                    g_score[neighbor] = tentative_g
                    heapq.heappush(open_set, (tentative_g + h(neighbor), neighbor))
        
        path_in2 = False
        if not path:
            # Retry on In2_Cu with no obstacles (since In2_Cu is empty!)
            open_set = []
            heapq.heappush(open_set, (0, start_pt))
            came_from = {}
            g_score = {start_pt: 0}
            while open_set:
                _, curr = heapq.heappop(open_set)
                if curr == end_pt:
                    path = [curr]
                    while curr in came_from:
                        curr = came_from[curr]
                        path.append(curr)
                    path.reverse()
                    break
                for dx, dy in [(-grid, 0), (grid, 0), (0, -grid), (0, grid)]:
                    neighbor = (curr[0] + dx, curr[1] + dy)
                    if neighbor[0] < min_x or neighbor[0] > max_x or neighbor[1] < min_y or neighbor[1] > max_y:
                        continue
                    tentative_g = g_score[curr] + grid
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        came_from[neighbor] = curr
                        g_score[neighbor] = tentative_g
                        heapq.heappush(open_set, (tentative_g + h(neighbor), neighbor))
            if path:
                path_in2 = True
                
        if not path:
            print(f"Failed to route {netname}")
            continue
            
        layer_to_use = pcbnew.In2_Cu if path_in2 else pcbnew.In1_Cu
        if not path_in2:
            for pt in path:
                obstacles.add(pt)
            
        # Draw Vias and stubs
        for p in (p1, p2):
            if not p['is_pth']:
                via = pcbnew.PCB_VIA(board)
                via.SetPosition(pcbnew.VECTOR2I(p['x'], p['y']))
                via.SetNetCode(netcode)
                via.SetViaType(pcbnew.VIATYPE_THROUGH)
                via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                via.SetWidth(mm(0.8))
                via.SetDrill(mm(0.4))
                board.Add(via)
                
            # short stub to snap point for BOTH SMD and PTH
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(p['x'], p['y']))
            t.SetEnd(pcbnew.VECTOR2I(snap(p['x']), snap(p['y'])))
            t.SetLayer(layer_to_use)
            t.SetNetCode(netcode)
            t.SetWidth(W)
            board.Add(t)
                
        # Draw path
        for j in range(len(path) - 1):
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(path[j][0], path[j][1]))
            t.SetEnd(pcbnew.VECTOR2I(path[j+1][0], path[j+1][1]))
            t.SetLayer(layer_to_use)
            t.SetNetCode(netcode)
            t.SetWidth(W)
            board.Add(t)

zf = pcbnew.ZONE_FILLER(board)
zf.Fill(board.Zones())
pcbnew.SaveBoard(board_path, board)
print("Routing completed!")
