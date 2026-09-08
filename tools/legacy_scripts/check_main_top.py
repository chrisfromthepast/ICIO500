import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

fps = re.findall(r'\(footprint\s+"([^"]+)"[\s\S]*?\(at\s+([0-9.-]+)\s+([0-9.-]+)(?:\s+([0-9.-]+))?\)', pcb)
for name, x, y, rot in fps:
    fx, fy = float(x), float(y)
    if 80 < fx < 120 and 150 < fy < 170:
        print(f"{name} at ({fx}, {fy}) rot={rot}")
