import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    c = f.read()

# Let's find all components and their bounding boxes
fps = []
for m in re.finditer(r'\(footprint\s+"([^"]+)".*?\(at\s+([\d\.-]+)\s+([\d\.-]+)(?:\s+([\d\.-]+))?\).*?\(property\s+"Reference"\s+"([^"]+)"', c, re.DOTALL):
    name = m.group(1)
    x = float(m.group(2))
    y = float(m.group(3))
    rot = float(m.group(4)) if m.group(4) else 0.0
    ref = m.group(5)
    fps.append((ref, name, x, y, rot))

print("Nearby components to U5 (X > 115):")
for ref, name, x, y, rot in sorted(fps, key=lambda t: t[2]):
    if x > 115 and ref != 'U5':
        print(f"  {ref:5s} at ({x:6.2f}, {y:6.2f}) : {name}")
