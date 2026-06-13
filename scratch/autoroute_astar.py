import pcbnew
import math
import heapq

def astar_route(board, start_pad, target_pos, target_net, track_width=0.25, clearance=0.25, layer=pcbnew.F_Cu):
    grid_size = 0.2  # mm
    
    # Bounding box
    min_x, max_x = 145.0, 185.0
    min_y, max_y = 75.0, 120.0
    
    grid_w = int((max_x - min_x) / grid_size) + 1
    grid_h = int((max_y - min_y) / grid_size) + 1
    
    obstacles = [[False for _ in range(grid_h)] for _ in range(grid_w)]
    
    def world_to_grid(x, y):
        return int((x - min_x) / grid_size), int((y - min_y) / grid_size)
    def grid_to_world(gx, gy):
        return min_x + gx * grid_size, min_y + gy * grid_size
        
    start_gx, start_gy = world_to_grid(start_pad.GetPosition().x/1e6, start_pad.GetPosition().y/1e6)
    target_gx, target_gy = world_to_grid(target_pos[0], target_pos[1])
    
    # Mark obstacles
    for pad in board.GetPads():
        if pad == start_pad: continue
        if pad.GetNetCode() == target_net and abs(pad.GetPosition().x/1e6 - target_pos[0]) < 0.1 and abs(pad.GetPosition().y/1e6 - target_pos[1]) < 0.1:
            continue
            
        px, py = pad.GetPosition().x/1e6, pad.GetPosition().y/1e6
        prx = max(pad.GetSize().x/1e6/2 + clearance, 0.4)
        pry = max(pad.GetSize().y/1e6/2 + clearance, 0.4)
        
        gx1, gy1 = world_to_grid(px - prx, py - pry)
        gx2, gy2 = world_to_grid(px + prx, py + pry)
        for i in range(max(0, gx1), min(grid_w, gx2+1)):
            for j in range(max(0, gy1), min(grid_h, gy2+1)):
                obstacles[i][j] = True
                
    for item in board.GetTracks():
        if item.GetLayer() != layer and not isinstance(item, pcbnew.PCB_VIA):
            continue
            
        if isinstance(item, pcbnew.PCB_VIA):
            width = 0.8
            sx, sy = item.GetPosition().x/1e6, item.GetPosition().y/1e6
            ex, ey = sx, sy
        else:
            try:
                width = item.GetWidth() / 1e6
            except:
                width = 0.25
            sx, sy = item.GetStart().x/1e6, item.GetStart().y/1e6
            ex, ey = item.GetEnd().x/1e6, item.GetEnd().y/1e6
            
        gx1, gy1 = world_to_grid(min(sx, ex) - clearance - width/2, min(sy, ey) - clearance - width/2)
        gx2, gy2 = world_to_grid(max(sx, ex) + clearance + width/2, max(sy, ey) + clearance + width/2)
        
        for i in range(max(0, gx1), min(grid_w, gx2+1)):
            for j in range(max(0, gy1), min(grid_h, gy2+1)):
                wx, wy = grid_to_world(i, j)
                l2 = (sx - ex)**2 + (sy - ey)**2
                if l2 == 0:
                    d = math.hypot(wx - sx, wy - sy)
                else:
                    t = max(0, min(1, ((wx - sx) * (ex - sx) + (wy - sy) * (ey - sy)) / l2))
                    proj_x = sx + t * (ex - sx)
                    proj_y = sy + t * (ey - sy)
                    d = math.hypot(wx - proj_x, wy - proj_y)
                if d < clearance + width/2:
                    obstacles[i][j] = True
                    
    # Ensure start and target are not obstacles
    obstacles[start_gx][start_gy] = False
    obstacles[target_gx][target_gy] = False
    
    open_set = []
    heapq.heappush(open_set, (0, start_gx, start_gy))
    came_from = {}
    g_score = {(start_gx, start_gy): 0}
    
    while open_set:
        _, curr_x, curr_y = heapq.heappop(open_set)
        
        if curr_x == target_gx and curr_y == target_gy:
            path = []
            curr = (curr_x, curr_y)
            while curr in came_from:
                path.append(curr)
                curr = came_from[curr]
            path.append((start_gx, start_gy))
            path.reverse()
            return [grid_to_world(x, y) for x, y in path]
            
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]:
            nx, ny = curr_x + dx, curr_y + dy
            if 0 <= nx < grid_w and 0 <= ny < grid_h and not obstacles[nx][ny]:
                # Penalize diagonal movement to favor straight lines
                tentative_g = g_score[(curr_x, curr_y)] + math.hypot(dx, dy) * (1.0 if dx==0 or dy==0 else 1.414)
                if tentative_g < g_score.get((nx, ny), float('inf')):
                    came_from[(nx, ny)] = (curr_x, curr_y)
                    g_score[(nx, ny)] = tentative_g
                    f_score = tentative_g + math.hypot(target_gx - nx, target_gy - ny)
                    heapq.heappush(open_set, (f_score, nx, ny))
                    
    return None

def simplify_path(path):
    if len(path) <= 2: return path
    simplified = [path[0]]
    for i in range(1, len(path)-1):
        prev = simplified[-1]
        curr = path[i]
        next_pt = path[i+1]
        # Check if they are collinear
        dx1, dy1 = curr[0]-prev[0], curr[1]-prev[1]
        dx2, dy2 = next_pt[0]-curr[0], next_pt[1]-curr[1]
        # normalize
        m1 = math.hypot(dx1, dy1)
        m2 = math.hypot(dx2, dy2)
        if m1>0 and m2>0 and abs(dx1/m1 - dx2/m2) < 0.01 and abs(dy1/m1 - dy2/m2) < 0.01:
            continue
        simplified.append(curr)
    simplified.append(path[-1])
    return simplified

def main():
    board_path = 'build/icio500/icio500.kicad_pcb'
    board = pcbnew.LoadBoard(board_path)
    
    c26 = board.FindFootprintByReference("C26")
    r3 = board.FindFootprintByReference("R3")
    u2 = board.FindFootprintByReference("U2")
    
    c26_p2 = c26.FindPadByNumber("2")
    r3_p1 = r3.FindPadByNumber("1")
    u2_p7 = u2.FindPadByNumber("7")
    
    print("Routing R3 to U2 on B.Cu...")
    path_audio = astar_route(board, r3_p1, (u2_p7.GetPosition().x/1e6, u2_p7.GetPosition().y/1e6), r3_p1.GetNetCode(), layer=pcbnew.B_Cu)
    
    if path_audio:
        path_audio = simplify_path(path_audio)
        print(f"Found audio path with {len(path_audio)} points")
        
        via1 = pcbnew.PCB_VIA(board)
        via1.SetPosition(r3_p1.GetPosition())
        via1.SetWidth(pcbnew.FromMM(0.6))
        via1.SetDrill(pcbnew.FromMM(0.3))
        via1.SetNetCode(r3_p1.GetNetCode())
        board.Add(via1)
        
        via2 = pcbnew.PCB_VIA(board)
        via2.SetPosition(u2_p7.GetPosition())
        via2.SetWidth(pcbnew.FromMM(0.6))
        via2.SetDrill(pcbnew.FromMM(0.3))
        via2.SetNetCode(u2_p7.GetNetCode())
        board.Add(via2)

        for i in range(len(path_audio)-1):
            track = pcbnew.PCB_TRACK(board)
            track.SetStart(pcbnew.VECTOR2I(int(path_audio[i][0]*1e6), int(path_audio[i][1]*1e6)))
            track.SetEnd(pcbnew.VECTOR2I(int(path_audio[i+1][0]*1e6), int(path_audio[i+1][1]*1e6)))
            track.SetWidth(pcbnew.FromMM(0.25))
            track.SetLayer(pcbnew.B_Cu)
            track.SetNetCode(r3_p1.GetNetCode())
            board.Add(track)
    else:
        print("Failed to route audio on B.Cu")
        
    print("Routing C26 to GND track at (170, 92.225) on B.Cu...")
    path_gnd = astar_route(board, c26_p2, (170.0, 92.225), c26_p2.GetNetCode(), layer=pcbnew.B_Cu)
    if path_gnd:
        path_gnd = simplify_path(path_gnd)
        print(f"Found GND path with {len(path_gnd)} points")
        
        via3 = pcbnew.PCB_VIA(board)
        via3.SetPosition(c26_p2.GetPosition())
        via3.SetWidth(pcbnew.FromMM(0.6))
        via3.SetDrill(pcbnew.FromMM(0.3))
        via3.SetNetCode(c26_p2.GetNetCode())
        board.Add(via3)
        
        via4 = pcbnew.PCB_VIA(board)
        via4.SetPosition(pcbnew.VECTOR2I(int(170.0*1e6), int(92.225*1e6)))
        via4.SetWidth(pcbnew.FromMM(0.6))
        via4.SetDrill(pcbnew.FromMM(0.3))
        via4.SetNetCode(c26_p2.GetNetCode())
        board.Add(via4)
        
        for i in range(len(path_gnd)-1):
            track = pcbnew.PCB_TRACK(board)
            track.SetStart(pcbnew.VECTOR2I(int(path_gnd[i][0]*1e6), int(path_gnd[i][1]*1e6)))
            track.SetEnd(pcbnew.VECTOR2I(int(path_gnd[i+1][0]*1e6), int(path_gnd[i+1][1]*1e6)))
            track.SetWidth(pcbnew.FromMM(0.25))
            track.SetLayer(pcbnew.B_Cu)
            track.SetNetCode(c26_p2.GetNetCode())
            board.Add(track)
    else:
        print("Failed to route GND on B.Cu")

    pcbnew.SaveBoard(board_path, board)
    print("Saved.")

if __name__ == '__main__':
    main()
