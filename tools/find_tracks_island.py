import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    content = f.read()

print('Tracks near the island:')
segments = re.finditer(r'\(segment\s+\(start\s+([\d.]+)\s+([\d.]+)\)\s+\(end\s+([\d.]+)\s+([\d.]+)\).*?\(layer\s+"([^"]+)".*?\(net\s+"([^"]+)"\)', content, re.DOTALL)
for m in segments:
    x1, y1, x2, y2 = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
    layer, net = m.group(5), m.group(6)
    
    # check if it passes through or near the box (98.5, 104.5) to (101.0, 107.0)
    # simple bounding box check
    min_x, max_x = min(x1, x2), max(x1, x2)
    min_y, max_y = min(y1, y2), max(y1, y2)
    
    if max_x >= 98.0 and min_x <= 101.5 and max_y >= 104.0 and min_y <= 107.5:
        print(f'{net} on {layer}: ({x1}, {y1}) to ({x2}, {y2})')
