import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    content = f.read()

segments = re.finditer(r'\(segment\s+\(start\s+([\d.]+)\s+([\d.]+)\)\s+\(end\s+([\d.]+)\s+([\d.]+)\).*?\(layer\s+"F.Cu".*?\(net\s+"([^"]+)"\)', content, re.DOTALL)
found = False
for m in segments:
    x1, y1, x2, y2 = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
    if max(x1, x2) >= 98.0 and min(x1, x2) <= 101.5 and max(y1, y2) >= 106.5 and min(y1, y2) <= 107.5:
        print(f'F.Cu track: ({x1}, {y1}) to ({x2}, {y2}) net {m.group(5)}')
        found = True
if not found:
    print('No F.Cu tracks found between pad 5 and 7!')
