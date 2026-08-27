import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the F.Cu GND zone (UUID: 6a2a9025-1cf9-46ab-a63d-ae791aae11c9)
ZONE_UUID = '6a2a9025-1cf9-46ab-a63d-ae791aae11c9'
uuid_pos = content.find(ZONE_UUID)
zone_start = content.rfind('\t(zone\n', 0, uuid_pos)

# find end of zone
depth = 0
zone_end = zone_start
for i in range(zone_start, min(zone_start + 500000, len(content))):
    if content[i] == '(': depth += 1
    elif content[i] == ')':
        depth -= 1
        if depth == 0:
            zone_end = i
            break

zone_block = content[zone_start:zone_end+1]

fp_matches = list(re.finditer(r'\t\t\(filled_polygon\n', zone_block))
print(f'Found {len(fp_matches)} polygons in F.Cu GND')

island_coords = []
for i, m in enumerate(fp_matches):
    fp_start = m.start()
    depth = 0
    fp_end = fp_start
    for j in range(fp_start, len(zone_block)):
        if zone_block[j] == '(': depth += 1
        elif zone_block[j] == ')':
            depth -= 1
            if depth == 0:
                fp_end = j
                break
    fp_block = zone_block[fp_start:fp_end+1]
    coords = re.findall(r'\(xy ([\d.-]+) ([\d.-]+)\)', fp_block)
    if not coords: continue
    xs = [float(x) for x, y in coords]
    if len(coords) < 150 and max(xs) - min(xs) < 5 and max(xs) > 96 and min(xs) < 104:
        island_coords = [(float(x), float(y)) for x, y in coords]
        print(f'Found island block {i}: {len(coords)} points')
        break

def point_in_polygon(x, y, poly):
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n+1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

if island_coords:
    # also we need check_clearance from previous script
    segments = []
    for m in re.finditer(r'\(segment\s+\(start\s+([\d.]+)\s+([\d.]+)\)\s+\(end\s+([\d.]+)\s+([\d.]+)\)', content, re.DOTALL):
        segments.append({
            'x1': float(m.group(1)), 'y1': float(m.group(2)),
            'x2': float(m.group(3)), 'y2': float(m.group(4))
        })
    pads = []
    for m in re.finditer(r'\(at\s+([\d.]+)\s+([\d.]+)(?:\s+[\d.]+)?\)', content):
        pads.append({'x': float(m.group(1)), 'y': float(m.group(2))})
    
    import math
    def dist_point_to_segment(px, py, x1, y1, x2, y2):
        l2 = (x1 - x2)**2 + (y1 - y2)**2
        if l2 == 0: return math.dist((px, py), (x1, y1))
        t = max(0, min(1, ((px - x1)*(x2 - x1) + (py - y1)*(y2 - y1)) / l2))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        return math.dist((px, py), (proj_x, proj_y))

    def check_clearance(px, py):
        min_dist = 9999
        for seg in segments:
            d = dist_point_to_segment(px, py, seg['x1'], seg['y1'], seg['x2'], seg['y2'])
            if d < min_dist: min_dist = d
        for pad in pads:
            d = math.dist((px, py), (pad['x'], pad['y']))
            if d < min_dist: min_dist = d
        return min_dist

    best_pt = None
    best_dist = 0
    xs = [p[0] for p in island_coords]
    ys = [p[1] for p in island_coords]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    x = min_x
    while x <= max_x:
        y = min_y
        while y <= max_y:
            if point_in_polygon(x, y, island_coords):
                d = check_clearance(x, y)
                if d > best_dist:
                    best_dist = d
                    best_pt = (x, y)
            y += 0.05
        x += 0.05
    print(f'Best via location INSIDE island: {best_pt} with clearance {best_dist:.2f}mm')
else:
    print('Island not found!')
