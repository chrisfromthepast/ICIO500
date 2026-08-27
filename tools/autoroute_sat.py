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

PCB_PATH = 'build/icio500/panel_satellite.kicad_pcb'
GRID_RESOLUTION = 0.05  # mm per grid cell
CLEARANCE = 0.1  # mm clearance from other nets
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
        
        pad_matches = list(re.finditer(r'\(pad "([^"]+)" ', fp_text))
        for pi, pm in enumerate(pad_matches):
            pad_num = pm.group(1)
            p_start = pm.start()
            p_end = pad_matches[pi + 1].start() if pi + 1 < len(pad_matches) else len(fp_text)
            pad_block = fp_text[p_start:p_end]
            
            at2 = re.search(r'\(at ([\d.e-]+) ([\d.e-]+)', pad_block)
            if not at2:
                continue
            px, py = float(at2.group(1)), float(at2.group(2))
            
            net_match = re.search(r'\(net (?:\d+ )?"([^"]+)"\)', pad_block)
            net = net_match.group(1) if net_match else None
            
            # Check if through-hole
            is_thru = 'thru_hole' in pad_block[:50]
            
            # Get pad size
            size_match = re.search(r'\(size ([\d.e-]+) ([\d.e-]+)\)', pad_block)
            pad_w = float(size_match.group(1)) if size_match else 1.6
            pad_h = float(size_match.group(2)) if size_match else 1.6
            
            abs_x = fp_x + px * cos_r - py * sin_r
            abs_y = fp_y + px * sin_r + py * cos_r
            
            pad_rot = 0.0
            try:
                if at2.lastindex and at2.lastindex >= 3:
                    pad_rot = float(at2.group(3))
            except:
                pass
                
            pads.append({
                'net': net, 'abs_x': round(abs_x, 4), 'abs_y': round(abs_y, 4),
                'ref': ref, 'pad_num': pad_num, 'is_thru': is_thru,
                'size_x': pad_w, 'size_y': pad_h,
                'layer': 'F.Cu' if 'F.Cu' in pad_block else 'B.Cu',
                'angle': fp_rot + pad_rot
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
    
    def __init__(self, bounds, resolution=GRID_RESOLUTION):
        self.bounds = bounds
        self.resolution = resolution
        self.min_x, self.min_y, self.max_x, self.max_y = bounds
        
        self.cols = int((self.max_x - self.min_x) / resolution) + 1
        self.rows = int((self.max_y - self.min_y) / resolution) + 1
        
        # grid[layer][(r, c)] = net_name (if occupied)
        self.grid = {'F.Cu': {}, 'B.Cu': {}}
        self.net_to_id = {}
    
    def populate_net_to_id(self, pcb_text):
        import re
        for match in re.finditer(r'\(net (\d+) "([^"]+)"\)', pcb_text[:5000]):
            self.net_to_id[match.group(2)] = int(match.group(1))   
    def xy_to_rc(self, x, y):
        col = int((x - self.min_x) / self.resolution)
        row = int((y - self.min_y) / self.resolution)
        return max(0, min(row, self.rows-1)), max(0, min(col, self.cols-1))
    
    def rc_to_xy(self, row, col):
        x = self.min_x + col * self.resolution
        y = self.min_y + row * self.resolution
        return x, y
    
    def mark_rect(self, layer, cx, cy, w, h, angle, net, clearance=0.0):
        """Mark a rotated rectangle in the grid."""
        import math
        # Simple bounding box for now to avoid complex math
        # Max radius is half diagonal
        diag = math.sqrt(w*w + h*h) / 2 + clearance
        # To prevent overlap with neighbors, we just mark the bounding box of the unrotated rect
        # if angle is 0, 90, 180, 270 (which all pads are)
        if abs(angle % 90) < 0.1:
            if abs(angle % 180) > 89:
                w, h = h, w
            min_x = cx - w/2 - clearance
            max_x = cx + w/2 + clearance
            min_y = cy - h/2 - clearance
            max_y = cy + h/2 + clearance
            
            min_c = max(0, int((min_x - self.min_x) / self.resolution))
            max_c = min(self.cols - 1, int((max_x - self.min_x) / self.resolution))
            min_r = max(0, int((min_y - self.min_y) / self.resolution))
            max_r = min(self.rows - 1, int((max_y - self.min_y) / self.resolution))
            
            for r in range(min_r, max_r + 1):
                for c in range(min_c, max_c + 1):
                    self.grid[layer][(r, c)] = net
        else:
            self.mark_circle(layer, cx, cy, diag, net)

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


def astar_route(grid, start_rc, start_layer, end_rc, end_layer, net, clearance_cells=1, max_iters=2000000):
    """A* pathfinding on the occupancy grid with via support."""
    sr, sc = start_rc
    er, ec = end_rc
    
    # Priority queue: (cost, row, col, layer)
    open_set = [(0, sr, sc, start_layer)]
    came_from = {}
    g_score = {(sr, sc, start_layer): 0}
    
    def heuristic(r, c, l):
        return abs(r - er) + abs(c - ec) + (0 if l == end_layer else 10.0)
    
    visited = set()
    iters = 0
    
    while open_set:
        iters += 1
        if iters > max_iters:
            print(f"      [A* limit reached ({max_iters})]")
            return None
        
        _, cr, cc, clayer = heapq.heappop(open_set)
        
        if (cr, cc, clayer) in visited:
            continue
        visited.add((cr, cc, clayer))
        
        if cr == er and cc == ec and clayer == end_layer:
            # Reconstruct path
            path = [(cr, cc, clayer)]
            while (cr, cc, clayer) in came_from:
                cr, cc, clayer = came_from[(cr, cc, clayer)]
                path.append((cr, cc, clayer))
            path.reverse()
            return path
        
        # 8-directional movement on same layer
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nr, nc = cr + dr, cc + dc
            if (nr, nc, clayer) in visited:
                continue
            if not grid.is_clear_with_clearance(clayer, nr, nc, net, clearance_cells):
                continue
            
            move_cost = 1.414 if (dr != 0 and dc != 0) else 1.0
            new_g = g_score[(cr, cc, clayer)] + move_cost
            
            if new_g < g_score.get((nr, nc, clayer), float('inf')):
                g_score[(nr, nc, clayer)] = new_g
                f = new_g + heuristic(nr, nc, clayer)
                came_from[(nr, nc, clayer)] = (cr, cc, clayer)
                heapq.heappush(open_set, (f, nr, nc, clayer))
                
        # Layer change (via)
        other_layer = 'B.Cu' if clayer == 'F.Cu' else 'F.Cu'
        if (cr, cc, other_layer) not in visited:
            if grid.is_clear_with_clearance(other_layer, cr, cc, net, clearance_cells):
                via_cost = 5.0
                new_g = g_score[(cr, cc, clayer)] + via_cost
                if new_g < g_score.get((cr, cc, other_layer), float('inf')):
                    g_score[(cr, cc, other_layer)] = new_g
                    f = new_g + heuristic(cr, cc, other_layer)
                    came_from[(cr, cc, other_layer)] = (cr, cc, clayer)
                    heapq.heappush(open_set, (f, cr, cc, other_layer))
    
    return None  # No path found

def simplify_path(path):
    """Convert grid 3D path to minimal segment list by merging collinear points on same layer."""
    if len(path) <= 2:
        return path
    
    simple = [path[0]]
    for i in range(1, len(path) - 1):
        prev = simple[-1]
        curr = path[i]
        nxt = path[i+1]
        
        if prev[2] != curr[2] or curr[2] != nxt[2]:
            simple.append(curr)
            continue
            
        dr1 = curr[0] - prev[0]
        dc1 = curr[1] - prev[1]
        dr2 = nxt[0] - curr[0]
        dc2 = nxt[1] - curr[1]
        
        if dr1 * dc2 != dr2 * dc1:
            simple.append(curr)
    
    simple.append(path[-1])
    return simple


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
    grid = OccupancyGrid((min_x, min_y, max_x, max_y), GRID_RESOLUTION)
    grid.populate_net_to_id(pcb_text)
    
    # Mark all pads (both layers for through-hole)
    for pad in pads:
        for layer in (['F.Cu', 'B.Cu'] if pad['is_thru'] else [pad['layer']]):
            grid.mark_rect(layer, pad['abs_x'], pad['abs_y'], pad['size_x'], pad['size_y'], pad['angle'], pad['net'], clearance=0.15)
    
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
    skip_nets = set()
    
    # Track which pads are completely unconnected
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
        
        # Routing
        clearance_cells = 2
        
        start_rc = grid.xy_to_rc(px, py)
        end_rc = grid.xy_to_rc(tx, ty)
        
        path = astar_route(grid, start_rc, 'F.Cu', end_rc, 'F.Cu', net, clearance_cells)
        if not path:
            path = astar_route(grid, start_rc, 'B.Cu', end_rc, 'F.Cu', net, clearance_cells)
        
        if path is None:
            print(f"    NO PATH FOUND!")
            continue
        
        # Simplify and convert to segments
        simple_path = simplify_path(path)
        print(f"    Path found: {len(path)} cells -> {len(simple_path)} waypoints")
        
        width = 0.4 if net in ('gnd', 'GND', 'v_plus', 'v_minus', 'daisy_5v_power', '+3V3', '+3V3_IN') else 0.25
        
        prev = simple_path[0]
        for curr in simple_path[1:]:
            sx, sy = grid.rc_to_xy(prev[0], prev[1])
            ex, ey = grid.rc_to_xy(curr[0], curr[1])
            
            if prev[2] != curr[2]:
                # Add via
                nid = next((nid for nn, nid in grid.net_to_id.items() if nn == net), 0)
                new_segments.append(f'  (via (at {sx:.3f} {sy:.3f}) (size 0.8) (drill 0.4) (layers "F.Cu" "B.Cu") (net {nid}))')
            else:
                # Add segment
                new_segments.append(make_segment(sx, sy, ex, ey, net, width, curr[2]))
                grid.mark_line(curr[2], sx, sy, ex, ey, width + CLEARANCE * 2, net)
            prev = curr
        
        # Update endpoints
        for r, c, l in simple_path:
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
