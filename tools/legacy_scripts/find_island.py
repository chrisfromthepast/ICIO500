"""
The isolated_copper island exists in the cached filled_polygon data on F.Cu.
The GND F.Cu zone (UUID 6a2a9025) has multiple filled_polygon entries.
We need to find and remove the isolated (disconnected) one.

The DRC says the island is near U6 pad 7 at (100.99, 107.0).
We'll find all filled_polygon blocks in the F.Cu GND zone and
identify which one is small / isolated (near that coordinate).
"""
import re

PCB = 'build/icio500/icio500.kicad_pcb'
content = open(PCB, encoding='utf-8').read()

ZONE_UUID = '6a2a9025-1cf9-46ab-a63d-ae791aae11c9'

# Find zone start
uuid_pos = content.find(ZONE_UUID)
zone_start = content.rfind('\t(zone\n', 0, uuid_pos)

# Find zone end
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
print(f'Zone block: {len(zone_block)} chars')

# Find all filled_polygon blocks within this zone
fp_matches = list(re.finditer(r'\t\t\(filled_polygon\n', zone_block))
print(f'Found {len(fp_matches)} filled_polygon blocks in F.Cu GND zone')

for i, m in enumerate(fp_matches):
    fp_start_in_zone = m.start()
    fp_abs = zone_start + fp_start_in_zone
    
    # Find block end
    depth = 0
    fp_end = fp_abs
    for j in range(fp_abs, min(fp_abs + 500000, len(content))):
        if content[j] == '(':
            depth += 1
        elif content[j] == ')':
            depth -= 1
            if depth == 0:
                fp_end = j
                break
    
    fp_block = content[fp_abs:fp_end+1]
    
    # Extract all xy coordinates to find bounding box
    coords = re.findall(r'\(xy ([\d.-]+) ([\d.-]+)\)', fp_block)
    if not coords:
        print(f'  Block {i}: no coords')
        continue
    
    xs = [float(x) for x, y in coords]
    ys = [float(y) for x, y in coords]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    width = x_max - x_min
    height = y_max - y_min
    area = width * height
    
    # Is it near U6 pad 7 at (100.99, 107.0)?
    near_u6 = (x_min < 105 and x_max > 96 and y_min < 111 and y_max > 103)
    
    print(f'  Block {i}: {len(coords)} pts, bbox=({x_min:.1f},{y_min:.1f})-({x_max:.1f},{y_max:.1f}), '
          f'size={width:.1f}x{height:.1f}mm, area~{area:.1f}mm2, near_U6={near_u6}')
    print(f'    chars: {len(fp_block)}, abs pos: {fp_abs}..{fp_end}')
