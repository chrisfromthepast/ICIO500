import re, math

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    content = f.read()

segments = []
for m in re.finditer(r'\(segment\s+\(start\s+([\d.]+)\s+([\d.]+)\)\s+\(end\s+([\d.]+)\s+([\d.]+)\)', content, re.DOTALL):
    segments.append({
        'x1': float(m.group(1)), 'y1': float(m.group(2)),
        'x2': float(m.group(3)), 'y2': float(m.group(4))
    })

pads = []
for m in re.finditer(r'\(at\s+([\d.]+)\s+([\d.]+)(?:\s+[\d.]+)?\)', content):
    pads.append({'x': float(m.group(1)), 'y': float(m.group(2))})

def dist_point_to_segment(px, py, x1, y1, x2, y2):
    l2 = (x1 - x2)**2 + (y1 - y2)**2
    if l2 == 0:
        return math.dist((px, py), (x1, y1))
    t = max(0, min(1, ((px - x1)*(x2 - x1) + (py - y1)*(y2 - y1)) / l2))
    proj_x = x1 + t * (x2 - x1)
    proj_y = y1 + t * (y2 - y1)
    return math.dist((px, py), (proj_x, proj_y))

def check_clearance(px, py):
    min_dist = 9999
    for seg in segments:
        d = dist_point_to_segment(px, py, seg['x1'], seg['y1'], seg['x2'], seg['y2'])
        if d < min_dist:
            min_dist = d
    for pad in pads:
        d = math.dist((px, py), (pad['x'], pad['y']))
        if d < min_dist:
            min_dist = d
    return min_dist

# Check a grid inside the island
best_pt = None
best_dist = 0
# The F.Cu island is approx x in [98.5, 101.0], y in [104.5, 107.0]
# But wait, we need to make sure the via is actually ON the F.Cu island!
# Let's check the island polygon points
fp_block = None
for m in re.finditer(r'\t\t\(filled_polygon\n.*?\(xy 99.75663 104.470253\).*?\)\n\t\t\)', content, re.DOTALL):
    fp_block = m.group(0)
    break

if not fp_block:
    # let's try finding the block more broadly
    print('Could not find island polygon exactly, using bounding box')
else:
    print('Found island polygon')

for x in [98.5 + i*0.1 for i in range(26)]:
    for y in [104.5 + i*0.1 for i in range(26)]:
        # A via with 0.8mm size needs at least 0.4 + 0.2 clearance = 0.6mm from center to anything
        d = check_clearance(x, y)
        if d > best_dist:
            best_dist = d
            best_pt = (x, y)

print(f'Best via location: {best_pt} with clearance {best_dist:.2f}mm')
