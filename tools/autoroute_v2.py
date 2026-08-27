"""
ICIO 500 Obstacle-Aware PCB Router v2
- Parses all pad locations, segments, vias, and zones
- Builds an occupancy grid for each copper layer
- Routes disconnected pads using A* pathfinding around obstacles
- Only routes GND pads that were identified as disconnected
"""
import re
import math
import uuid
import heapq
from collections import defaultdict

PCB_PATH = 'build/icio500/icio500.kicad_pcb'
GRID_RESOLUTION = 0.254  # mm per grid cell (10 mil)
CLEARANCE = 0.3  # mm clearance from other nets
TRACE_WIDTH = 0.3  # mm

def parse_footprint_pads(pcb_text):
    """Extract absolute pad positions from all footprints."""
    pads = []
    fp_starts = [m.start() for m in re.finditer(r'\n\t\(footprint ', pcb_text)]
    
    for idx in range(len(fp_starts)):
        start = fp_starts[idx]
        end = fp_starts[idx + 1] if idx + 1 < len(fp_starts) else len(pcb_text)
        fp_text = pcb_text[start:end]
        
        at_match = re.search(r'\n\t\t\(at ([\d.e-]+) ([\d.e-]+)(?: ([\d.e-]+))?\)', fp_text)
        if not at_match:
            continue
        fp_x = float(at_match.group(1))
        fp_y = float(at_match.group(2))
        fp_rot = float(at_match.group(3)) if at_match.group(3) else 0.0
        
        ref_match = re.search(r'"Reference" "([^"]+)"', fp_text[:1500])
        ref = ref_match.group(1) if ref_match else '??'
        
        rot_rad = math.radians(-fp_rot)
        cos_r = math.cos(rot_rad)
        sin_r = math.sin(rot_rad)
        
        pad_matches = list(re.finditer(r'\(pad "(\d+)" ', fp_text))
        for pi, pm in enumerate(pad_matches):
            pad_num = pm.group(1)
            p_start = pm.start()
            p_end = pad_matches[pi + 1].start() if pi + 1 < len(pad_matches) else len(fp_text)
            pad_block = fp_text[p_start:p_end]
            
            at2 = re.search(r'\(at ([\d.e-]+) ([\d.e-]+)', pad_block)
            if not at2:
                continue
            px, py = float(at2.group(1)), float(at2.group(2))
            
            net_match = re.search(r'\(net "([^"]+)"\)', pad_block)
            net = net_match.group(1) if net_match else None
            
            # Check if through-hole
            is_thru = 'thru_hole' in pad_block[:50]
            
            # Get pad size
            size_match = re.search(r'\(size ([\d.e-]+) ([\d.e-]+)\)', pad_block)
            pad_w = float(size_match.group(1)) if size_match else 1.6
            pad_h = float(size_match.group(2)) if size_match else 1.6
            
            abs_x = fp_x + px * cos_r - py * sin_r
            abs_y = fp_y + px * sin_r + py * cos_r
            
            pads.append({
                'net': net, 'abs_x': round(abs_x, 4), 'abs_y': round(abs_y, 4),
                'ref': ref, 'pad_num': pad_num, 'is_thru': is_thru,
                'width': pad_w, 'height': pad_h,
            })
    return pads


def parse_segments(pcb_text):
    """Parse all trace segments."""
    segments = []
    for m in re.finditer(
        r'\(segment\s+\(start ([\d.e-]+) ([\d.e-]+)\)\s+\(end ([\d.e-]+) ([\d.e-]+)\)\s+\(width ([\d.e-]+)\)\s+\(layer "([^"]+)"\)\s+\(net "([^"]+)"\)',
        pcb_text
    ):
        segments.append({
            'sx': float(m.group(1)), 'sy': float(m.group(2)),
            'ex': float(m.group(3)), 'ey': float(m.group(4)),
            'width': float(m.group(5)), 'layer': m.group(6), 'net': m.group(7),
        })
    return segments


def parse_vias(pcb_text):
    """Parse all vias."""
    vias = []
    for m in re.finditer(
        r'\(via\s+\(at ([\d.e-]+) ([\d.e-]+)\)\s+\(size ([\d.e-]+)\).*?\(net "([^"]+)"\)',
        pcb_text, re.DOTALL
    ):
        vias.append({
            'x': float(m.group(1)), 'y': float(m.group(2)),
            'size': float(m.group(3)), 'net': m.group(4),
        })
    return vias


class OccupancyGrid:
    """2D grid that tracks which cells are occupied by copper on each layer."""
    
    def __init__(self, min_x, min_y, max_x, max_y, resolution):
        self.min_x = min_x
        self.min_y = min_y
        self.resolution = resolution
        self.cols = int((max_x - min_x) / resolution) + 2
        self.rows = int((max_y - min_y) / resolution) + 2
        # grid[layer][(row, col)] = net_name
        self.grid = defaultdict(dict)
    
    def xy_to_rc(self, x, y):
        col = int((x - self.min_x) / self.resolution)
        row = int((y - self.min_y) / self.resolution)
        return max(0, min(row, self.rows-1)), max(0, min(col, self.cols-1))
    
    def rc_to_xy(self, row, col):
        x = self.min_x + col * self.resolution
        y = self.min_y + row * self.resolution
        return x, y
    
    def mark_circle(self, layer, cx, cy, radius, net):
        """Mark a circular area as occupied."""
        r1, c1 = self.xy_to_rc(cx - radius, cy - radius)
        r2, c2 = self.xy_to_rc(cx + radius, cy + radius)
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                x, y = self.rc_to_xy(r, c)
                if (x - cx)**2 + (y - cy)**2 <= radius**2:
                    self.grid[layer][(r, c)] = net
    
    def mark_line(self, layer, x1, y1, x2, y2, width, net):
        """Mark a line segment with given width as occupied."""
        length = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        if length < 0.001:
            self.mark_circle(layer, x1, y1, width/2, net)
            return
        
        dx = (x2 - x1) / length
        dy = (y2 - y1) / length
        steps = int(length / self.resolution) + 1
        
        for i in range(steps + 1):
            t = i / max(steps, 1)
            cx = x1 + t * (x2 - x1)
            cy = y1 + t * (y2 - y1)
            self.mark_circle(layer, cx, cy, width/2, net)
    
    def is_clear(self, layer, row, col, target_net):
        """Check if a cell is clear for routing a given net."""
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False
        occupant = self.grid[layer].get((row, col))
        if occupant is None:
            return True
        return occupant == target_net  # OK to overlap same net
    
    def is_clear_with_clearance(self, layer, row, col, target_net, clearance_cells=1):
        """Check cell and neighbors for clearance."""
        for dr in range(-clearance_cells, clearance_cells + 1):
            for dc in range(-clearance_cells, clearance_cells + 1):
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    occupant = self.grid[layer].get((nr, nc))
                    if occupant is not None and occupant != target_net:
                        return False
        return True


def astar_route(grid, layer, start_rc, end_rc, net, clearance_cells=1):
    """A* pathfinding on the occupancy grid."""
    sr, sc = start_rc
    er, ec = end_rc
    
    # Priority queue: (cost, row, col)
    open_set = [(0, sr, sc)]
    came_from = {}
    g_score = {(sr, sc): 0}
    
    def heuristic(r, c):
        return abs(r - er) + abs(c - ec)  # Manhattan distance
    
    visited = set()
    
    while open_set:
        _, cr, cc = heapq.heappop(open_set)
        
        if (cr, cc) in visited:
            continue
        visited.add((cr, cc))
        
        if cr == er and cc == ec:
            # Reconstruct path
            path = [(cr, cc)]
            while (cr, cc) in came_from:
                cr, cc = came_from[(cr, cc)]
                path.append((cr, cc))
            path.reverse()
            return path
        
        # 8-directional movement
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nr, nc = cr + dr, cc + dc
            if (nr, nc) in visited:
                continue
            if not grid.is_clear_with_clearance(layer, nr, nc, net, clearance_cells):
                continue
            
            move_cost = 1.414 if (dr != 0 and dc != 0) else 1.0
            new_g = g_score[(cr, cc)] + move_cost
            
            if new_g < g_score.get((nr, nc), float('inf')):
                g_score[(nr, nc)] = new_g
                f = new_g + heuristic(nr, nc)
                came_from[(nr, nc)] = (cr, cc)
                heapq.heappush(open_set, (f, nr, nc))
    
    return None  # No path found


def simplify_path(path):
    """Convert grid path to minimal segment list by merging collinear points."""
    if len(path) <= 2:
        return path
    
    simplified = [path[0]]
    for i in range(1, len(path) - 1):
        prev = path[i - 1]
        curr = path[i]
        next_pt = path[i + 1]
        
        # Check if collinear
        dr1 = curr[0] - prev[0]
        dc1 = curr[1] - prev[1]
        dr2 = next_pt[0] - curr[0]
        dc2 = next_pt[1] - curr[1]
        
        if (dr1, dc1) != (dr2, dc2):
            simplified.append(curr)
    
    simplified.append(path[-1])
    return simplified


def make_segment(sx, sy, ex, ey, net, width, layer):
    uid = str(uuid.uuid4())
    return (
        f'\t(segment\n'
        f'\t\t(start {sx:.4f} {sy:.4f})\n'
        f'\t\t(end {ex:.4f} {ey:.4f})\n'
        f'\t\t(width {width})\n'
        f'\t\t(layer "{layer}")\n'
        f'\t\t(net "{net}")\n'
        f'\t\t(uuid "{uid}")\n'
        f'\t)\n'
    )


def main():
    print("Loading PCB...")
    with open(PCB_PATH, encoding='utf-8') as f:
        pcb_text = f.read()
    
    pads = parse_footprint_pads(pcb_text)
    segments = parse_segments(pcb_text)
    vias = parse_vias(pcb_text)
    
    print(f"  {len(pads)} pads, {len(segments)} segments, {len(vias)} vias")
    
    # Determine board bounds
    all_x = [p['abs_x'] for p in pads] + [s['sx'] for s in segments] + [s['ex'] for s in segments]
    all_y = [p['abs_y'] for p in pads] + [s['sy'] for s in segments] + [s['ey'] for s in segments]
    min_x, max_x = min(all_x) - 5, max(all_x) + 5
    min_y, max_y = min(all_y) - 5, max(all_y) + 5
    
    print(f"  Board bounds: ({min_x:.1f}, {min_y:.1f}) to ({max_x:.1f}, {max_y:.1f})")
    
    # Build occupancy grids
    print("Building occupancy grids...")
    grid = OccupancyGrid(min_x, min_y, max_x, max_y, GRID_RESOLUTION)
    
    # Mark all pads (both layers for through-hole)
    for pad in pads:
        net = pad['net'] or '__nonet__'
        radius = max(pad['width'], pad['height']) / 2 + CLEARANCE
        grid.mark_circle('F.Cu', pad['abs_x'], pad['abs_y'], radius, net)
        if pad['is_thru']:
            grid.mark_circle('B.Cu', pad['abs_x'], pad['abs_y'], radius, net)
    
    # Mark all segments
    for seg in segments:
        half_w = seg['width'] / 2 + CLEARANCE
        grid.mark_line(seg['layer'], seg['sx'], seg['sy'], seg['ex'], seg['ey'], 
                      seg['width'] + CLEARANCE * 2, seg['net'])
    
    # Mark all vias (both layers)
    for via in vias:
        radius = via['size'] / 2 + CLEARANCE
        grid.mark_circle('F.Cu', via['x'], via['y'], radius, via['net'])
        grid.mark_circle('B.Cu', via['x'], via['y'], radius, via['net'])
    
    print("  Occupancy grids built.")
    
    # Find disconnected pads
    print("\nFinding disconnected pads...")
    net_endpoints = defaultdict(set)
    for seg in segments:
        net_endpoints[seg['net']].add((round(seg['sx'], 2), round(seg['sy'], 2)))
        net_endpoints[seg['net']].add((round(seg['ex'], 2), round(seg['ey'], 2)))
    for via in vias:
        net_endpoints[via['net']].add((round(via['x'], 2), round(via['y'], 2)))
    
    TOLERANCE = 0.6
    skip_nets = {'audio_out_r', 'p18', 'p19', 'p20'}
    disconnected = []
    
    for pad in pads:
        if not pad['net'] or pad['net'] in skip_nets:
            continue
        endpoints = net_endpoints.get(pad['net'], set())
        px, py = pad['abs_x'], pad['abs_y']
        found = any(abs(px - ex) < TOLERANCE and abs(py - ey) < TOLERANCE 
                    for ex, ey in endpoints)
        if not found:
            disconnected.append(pad)
    
    print(f"  Found {len(disconnected)} disconnected pads")
    
    # Find routing targets (nearest existing endpoint on same net)
    clearance_cells = max(1, int(CLEARANCE / GRID_RESOLUTION))
    new_segments = []
    
    for pad in disconnected:
        net = pad['net']
        px, py = pad['abs_x'], pad['abs_y']
        
        # Find nearest existing connected point on same net
        best_target = None
        best_dist = float('inf')
        for ex, ey in net_endpoints.get(net, set()):
            dist = math.sqrt((px - ex)**2 + (py - ey)**2)
            if dist < best_dist and dist > TOLERANCE:
                best_dist = dist
                best_target = (ex, ey)
        
        if not best_target:
            # Try nearest pad on same net
            for other in pads:
                if other['net'] != net:
                    continue
                ox, oy = other['abs_x'], other['abs_y']
                dist = math.sqrt((px - ox)**2 + (py - oy)**2)
                if dist < best_dist and dist > TOLERANCE:
                    best_dist = dist
                    best_target = (ox, oy)
        
        if not best_target:
            print(f"  SKIP {pad['ref']} pad {pad['pad_num']} ({net}) - no target")
            continue
        
        tx, ty = best_target
        print(f"  Routing {pad['ref']} pad {pad['pad_num']} ({net}): ({px:.1f},{py:.1f}) -> ({tx:.1f},{ty:.1f}) dist={best_dist:.1f}mm")
        
        # Try F.Cu first, then B.Cu for through-hole pads
        start_rc = grid.xy_to_rc(px, py)
        end_rc = grid.xy_to_rc(tx, ty)
        
        path = astar_route(grid, 'F.Cu', start_rc, end_rc, net, clearance_cells)
        layer = 'F.Cu'
        
        if path is None and pad['is_thru']:
            print(f"    F.Cu blocked, trying B.Cu...")
            path = astar_route(grid, 'B.Cu', start_rc, end_rc, net, clearance_cells)
            layer = 'B.Cu'
        
        if path is None:
            print(f"    NO PATH FOUND!")
            continue
        
        # Simplify and convert to segments
        simple_path = simplify_path(path)
        print(f"    Path found: {len(path)} cells -> {len(simple_path)} waypoints on {layer}")
        
        width = 0.4 if net in ('gnd', 'v_plus', 'v_minus', 'daisy_5v_power') else 0.25
        
        for i in range(len(simple_path) - 1):
            sx, sy = grid.rc_to_xy(*simple_path[i])
            ex, ey = grid.rc_to_xy(*simple_path[i + 1])
            new_segments.append(make_segment(sx, sy, ex, ey, net, width, layer))
            # Mark new segment on grid
            grid.mark_line(layer, sx, sy, ex, ey, width + CLEARANCE * 2, net)
        
        # Update endpoints
        for r, c in simple_path:
            x, y = grid.rc_to_xy(r, c)
            net_endpoints[net].add((round(x, 2), round(y, 2)))
    
    if not new_segments:
        print("\nNo new segments to add!")
        return
    
    print(f"\n=== WRITING {len(new_segments)} NEW SEGMENTS ===")
    new_text = '\n'.join(new_segments)
    insert_pos = pcb_text.rfind('\n)')
    pcb_text = pcb_text[:insert_pos] + '\n' + new_text + pcb_text[insert_pos:]
    
    with open(PCB_PATH, 'w', encoding='utf-8') as f:
        f.write(pcb_text)
    
    print(f"Saved to {PCB_PATH}")


if __name__ == '__main__':
    main()
