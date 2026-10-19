import heapq
import math

class GridRouter:
    def __init__(self, x_min=50.0, x_max=115.0, y_min=75.0, y_max=145.0, step=0.5):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.step = step
        self.nx = int(round((x_max - x_min) / step)) + 1
        self.ny = int(round((y_max - y_min) / step)) + 1
        # 2 layers: 0=F.Cu, 1=B.Cu
        # 0 = free, 1 = blocked
        self.grid = [
            [[False for _ in range(self.ny)] for _ in range(self.nx)],
            [[False for _ in range(self.ny)] for _ in range(self.nx)]
        ]
        self.paths = []

    def to_grid(self, x, y):
        gx = int(round((x - self.x_min) / self.step))
        gy = int(round((y - self.y_min) / self.step))
        return gx, gy

    def to_world(self, gx, gy):
        x = self.x_min + gx * self.step
        y = self.y_min + gy * self.step
        return round(x, 3), round(y, 3)

    def block_circle(self, layer, cx, cy, radius):
        gx, gy = self.to_grid(cx, cy)
        gr = int(math.ceil(radius / self.step))
        for x in range(max(0, gx - gr), min(self.nx, gx + gr + 1)):
            for y in range(max(0, gy - gr), min(self.ny, gy + gr + 1)):
                wx, wy = self.to_world(x, y)
                if (wx - cx)**2 + (wy - cy)**2 <= radius**2:
                    self.grid[layer][x][y] = True

    def block_rect(self, layer, x1, y1, x2, y2):
        gx1, gy1 = self.to_grid(min(x1, x2), min(y1, y2))
        gx2, gy2 = self.to_grid(max(x1, x2), max(y1, y2))
        for x in range(max(0, gx1), min(self.nx, gx2 + 1)):
            for y in range(max(0, gy1), min(self.ny, gy2 + 1)):
                self.grid[layer][x][y] = True

    def route_net(self, start, end, layer, clearance=0.5):
        # A* on single layer
        sx, sy = self.to_grid(start[0], start[1])
        ex, ey = self.to_grid(end[0], end[1])
        
        # Priority queue: (f_score, cost, (x, y), path)
        open_set = []
        heapq.heappush(open_set, (0, 0, (sx, sy), [(sx, sy)]))
        visited = { (sx, sy): 0 }
        
        moves = [
            (1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
            (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)
        ]
        
        found_path = None
        while open_set:
            f, cost, (cx, cy), path = heapq.heappop(open_set)
            if (cx, cy) == (ex, ey):
                found_path = path
                break
                
            for dx, dy, move_cost in moves:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.nx and 0 <= ny < self.ny:
                    # check if blocked (allow target point)
                    if self.grid[layer][nx][ny] and (nx, ny) != (ex, ey):
                        continue
                    new_cost = cost + move_cost
                    if (nx, ny) not in visited or new_cost < visited[(nx, ny)]:
                        visited[(nx, ny)] = new_cost
                        # heuristic: octile distance
                        hdx = abs(nx - ex)
                        hdy = abs(ny - ey)
                        h = max(hdx, hdy) + 0.414 * min(hdx, hdy)
                        heapq.heappush(open_set, (new_cost + h * 1.05, new_cost, (nx, ny), path + [(nx, ny)]))
                        
        if not found_path:
            return None
            
        # Convert path to world points and block clearance around it
        world_path = [self.to_world(x, y) for x, y in found_path]
        for wx, wy in world_path:
            self.block_circle(layer, wx, wy, clearance)
        return world_path

print("GridRouter initialized successfully.")
