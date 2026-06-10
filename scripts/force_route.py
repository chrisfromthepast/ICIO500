import pcbnew
import math
import heapq

G = 0.25 # 0.25mm grid
def mm(v): return int(v * 1_000_000)

board_path = 'build/icio500/icio500.kicad_pcb'
board = pcbnew.LoadBoard(board_path)

def dist(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

print("Mapping obstacles on In1.Cu...")
obstacles = set()
for fp in board.GetFootprints():
    for p in fp.Pads():
        # Only through-hole pads are obstacles on inner layers
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
            px = p.GetPosition().x / 1e6
            py = p.GetPosition().y / 1e6
            sx = (p.GetSize().x / 1e6) / 2
            sy = (p.GetSize().y / 1e6) / 2
            
            min_x = int(math.floor((px - sx) / G)) - 2
            max_x = int(math.ceil((px + sx) / G)) + 2
            min_y = int(math.floor((py - sy) / G)) - 2
            max_y = int(math.ceil((py + sy) / G)) + 2
            
            for gx in range(min_x, max_x + 1):
                for gy in range(min_y, max_y + 1):
                    obstacles.add((gx, gy))

# Also add existing vias as obstacles
for t in board.GetTracks():
    if isinstance(t, pcbnew.PCB_VIA):
        px = t.GetPosition().x / 1e6
        py = t.GetPosition().y / 1e6
        r = 0.4
        min_x = int(math.floor((px - r) / G)) - 2
        max_x = int(math.ceil((px + r) / G)) + 2
        min_y = int(math.floor((py - r) / G)) - 2
        max_y = int(math.ceil((py + r) / G)) + 2
        for gx in range(min_x, max_x + 1):
            for gy in range(min_y, max_y + 1):
                obstacles.add((gx, gy))

def astar(start, end):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    
    expansions = 0
    min_bx = min(start[0], end[0]) - 60
    max_bx = max(start[0], end[0]) + 60
    min_by = min(start[1], end[1]) - 60
    max_by = max(start[1], end[1]) + 60
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]
            
        expansions += 1
        if expansions > 20000:
            print("  -> FAILED (too many expansions)")
            return None
            
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0), (1,1), (-1,1), (1,-1), (-1,-1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            
            if neighbor[0] < min_bx or neighbor[0] > max_bx or neighbor[1] < min_by or neighbor[1] > max_by:
                continue
                
            if neighbor in obstacles:
                if dist(neighbor, start) <= 6 or dist(neighbor, end) <= 6:
                    pass
                else:
                    continue
                    
            move_cost = 1.414 if dx != 0 and dy != 0 else 1.0
            tentative_g = g_score[current] + move_cost
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + dist(neighbor, end)
                heapq.heappush(open_set, (f_score, neighbor))
                
    return None

nets_to_skip = ['', 'gnd', 'chassis_gnd', 'v_plus_16v', 'v_minus_16v', 'v_plus_48v', 'daisy_digital_gnd', 'daisy_5v_power']

# Get all nets
all_nets = board.GetNetsByName()
for netname_wx, net in all_nets.items():
    netname = str(netname_wx)
    if not netname or netname in nets_to_skip:
        continue
        
    pads = [p for fp in board.GetFootprints() for p in fp.Pads() if p.GetNetname() == netname]
    if len(pads) < 2:
        continue
        
    # Remove existing tracks for this net to reroute clean
    for t in list(board.GetTracks()):
        if t.GetNetname() == netname:
            board.Remove(t)
            
    # Skip sorting to avoid Swig object errors
    
    print(f"Routing {netname} ({len(pads)} pads)...")
    for i in range(len(pads) - 1):
        p1 = pads[i]
        p2 = pads[i+1]
        
        v1 = pcbnew.VECTOR2I(p1.GetPosition())
        v2 = pcbnew.VECTOR2I(p2.GetPosition())
        start_pos = (int((v1.x/1e6)/G), int((v1.y/1e6)/G))
        end_pos = (int((v2.x/1e6)/G), int((v2.y/1e6)/G))
        
        print(f"  {start_pos} to {end_pos}...")
        path = astar(start_pos, end_pos)
        if path:
            # Draw vias at start and end if they are SMD
            if p1.GetAttribute() != pcbnew.PAD_ATTRIB_PTH:
                via = pcbnew.PCB_VIA(board)
                via.SetPosition(p1.GetPosition())
                via.SetNetCode(net.GetNetCode())
                via.SetViaType(pcbnew.VIATYPE_THROUGH)
                via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                via.SetWidth(mm(0.8))
                via.SetDrill(mm(0.4))
                board.Add(via)
                # Micro-track to guarantee connection
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(p1.GetPosition())
                t.SetEnd(p1.GetPosition())
                t.SetLayer(p1.GetLayer())
                t.SetNetCode(net.GetNetCode())
                t.SetWidth(mm(0.25))
                board.Add(t)

            if p2.GetAttribute() != pcbnew.PAD_ATTRIB_PTH:
                via2 = pcbnew.PCB_VIA(board)
                via2.SetPosition(p2.GetPosition())
                via2.SetNetCode(net.GetNetCode())
                via2.SetViaType(pcbnew.VIATYPE_THROUGH)
                via2.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                via2.SetWidth(mm(0.8))
                via2.SetDrill(mm(0.4))
                board.Add(via2)
                # Micro-track to guarantee connection
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(p2.GetPosition())
                t.SetEnd(p2.GetPosition())
                t.SetLayer(p2.GetLayer())
                t.SetNetCode(net.GetNetCode())
                t.SetWidth(mm(0.25))
                board.Add(t)
                
            # Draw track on In1_Cu
            for j in range(len(path) - 1):
                pt1 = path[j]
                pt2 = path[j+1]
                track = pcbnew.PCB_TRACK(board)
                track.SetStart(pcbnew.VECTOR2I(mm(pt1[0]*G), mm(pt1[1]*G)))
                track.SetEnd(pcbnew.VECTOR2I(mm(pt2[0]*G), mm(pt2[1]*G)))
                track.SetWidth(mm(0.25))
                track.SetLayer(pcbnew.In1_Cu)
                track.SetNetCode(net.GetNetCode())
                board.Add(track)
                
                # add to obstacles
                obstacles.add(pt1)
                obstacles.add(pt2)
            print("  -> SUCCESS")
            pcbnew.SaveBoard(board_path, board)
        else:
            print("  -> FAILED")

# Zone fill
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

pcbnew.SaveBoard(board_path, board)
print("Done!")
