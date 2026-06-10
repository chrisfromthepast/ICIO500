import pcbnew
import os
import math
import heapq

G = 0.25 # 0.25mm grid

def mm(v): return int(v * 1_000_000)

def seg(board, net, x0, y0, x1, y1, w=0.5, lyr=pcbnew.F_Cu):
    if abs(x0-x1) < 0.01 and abs(y0-y1) < 0.01: return
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(mm(x0), mm(y0)))
    t.SetEnd(  pcbnew.VECTOR2I(mm(x1), mm(y1)))
    t.SetWidth(mm(w))
    t.SetLayer(lyr)
    if net: t.SetNet(net)
    board.Add(t)

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def dist(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

def a_star(start, end, obstacles):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        
        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path
            
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            
            # Bounds check (X: 50 to 195, Y: 55 to 160) -> G=0.25 means (200 to 780, 220 to 640)
            if neighbor[0] < 180 or neighbor[0] > 800 or neighbor[1] < 200 or neighbor[1] > 660:
                continue
                
            if neighbor in obstacles:
                if dist(neighbor, start) <= 8 or dist(neighbor, end) <= 8:
                    pass
                else:
                    continue
                
            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, end)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
                
    return None

def build_obstacles(board):
    obstacles = set()
    
    # Add pads
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if not p.IsOnLayer(pcbnew.F_Cu):
                continue
            # Pad center
            px = p.GetPosition().x / 1e6
            py = p.GetPosition().y / 1e6
            # Approximate pad size
            sx = p.GetSize().x / 1e6 / 2
            sy = p.GetSize().y / 1e6 / 2
            
            min_x = int(math.floor((px - sx) / G)) - 1
            max_x = int(math.ceil((px + sx) / G)) + 1
            min_y = int(math.floor((py - sy) / G)) - 1
            max_y = int(math.ceil((py + sy) / G)) + 1
            
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    obstacles.add((x, y))
                    
    # Add tracks
    for t in board.GetTracks():
        if t.GetLayer() != pcbnew.F_Cu:
            continue
        x0 = t.GetStart().x / 1e6
        y0 = t.GetStart().y / 1e6
        x1 = t.GetEnd().x / 1e6
        y1 = t.GetEnd().y / 1e6
        
        d = math.hypot(x1 - x0, y1 - y0)
        steps = int(d / (G / 2)) + 1
        for i in range(steps + 1):
            t_ratio = i / steps if steps > 0 else 0
            cx = x0 + t_ratio * (x1 - x0)
            cy = y0 + t_ratio * (y1 - y0)
            gx = int(round(cx / G))
            gy = int(round(cy / G))
            obstacles.add((gx, gy))
                    
    return obstacles

def apply_autoroute():
    pcb_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "build", "icio500", "icio500.kicad_pcb"
    )
    board = pcbnew.LoadBoard(pcb_path)
    print("Board loaded for A* Autorouting.")
    
    obstacles = build_obstacles(board)
    print(f"Mapped {len(obstacles)} obstacle grid cells.")
    
    nets_to_route = [
        'daisy_audio_in',
        'daisy_audio_out',
        'daisy_d13',
        'daisy_d14',
        'daisy_5v_power'
    ]
    
    for net_name in nets_to_route:
        net = board.FindNet(net_name)
        if not net: continue
        
        pts = []
        for fp in board.GetFootprints():
            for p in fp.Pads():
                if p.GetNetname() == net_name:
                    pts.append((p.GetPosition().x / 1e6, p.GetPosition().y / 1e6))
        pts.sort() # simple left-to-right sorting
        
        for i in range(len(pts) - 1):
            start_real = pts[i]
            end_real = pts[i+1]
            
            start_grid = (int(round(start_real[0] / G)), int(round(start_real[1] / G)))
            end_grid = (int(round(end_real[0] / G)), int(round(end_real[1] / G)))
            
            print(f"Routing {net_name} from {start_grid} to {end_grid}...")
            path = a_star(start_grid, end_grid, obstacles)
            
            if path:
                # simplify path
                simplified = [path[0]]
                for j in range(1, len(path)-1):
                    prev = path[j-1]
                    curr = path[j]
                    nxt = path[j+1]
                    if (curr[0]-prev[0] == nxt[0]-curr[0]) and (curr[1]-prev[1] == nxt[1]-curr[1]):
                        continue
                    simplified.append(curr)
                simplified.append(path[-1])
                
                real_pts = [start_real] + [(p[0]*G, p[1]*G) for p in simplified] + [end_real]
                for j in range(len(real_pts)-1):
                    w = 1.0 if "power" in net_name else 0.5
                    seg(board, net, real_pts[j][0], real_pts[j][1], real_pts[j+1][0], real_pts[j+1][1], w=w, lyr=pcbnew.F_Cu)
                    
                # mark path as obstacle
                for p in path:
                    obstacles.add((p[0], p[1]))
                print(f"  -> SUCCESS.")
            else:
                print(f"  -> FAILED.")
                
    pcbnew.SaveBoard(pcb_path, board)
    print("A* routing complete.")

if __name__ == '__main__':
    apply_autoroute()
