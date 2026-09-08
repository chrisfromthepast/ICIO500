import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

fps = re.findall(r'\(footprint\s+"([^"]+)"[\s\S]*?\(at\s+([0-9.-]+)\s+([0-9.-]+)(?:\s+([0-9.-]+))?\)', pcb)
for name, x, y, rot in fps:
    fx, fy = float(x), float(y)
    if 85 < fx < 105 and 90 < fy < 120:
        print(f"{name} at ({fx}, {fy}) rot={rot}")
