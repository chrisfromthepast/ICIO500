import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    content = f.read()

print("--- Edge.Cuts Lines ---")
for m in re.finditer(r'\(gr_line\s+\(start\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(end\s+([\d\.-]+)\s+([\d\.-]+)\).*?\(layer\s+"?Edge\.Cuts"?\)', content, re.DOTALL):
    print(f"Line: ({m.group(1)}, {m.group(2)}) -> ({m.group(3)}, {m.group(4)})")

for m in re.finditer(r'\(gr_arc\s+\(start\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(mid\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(end\s+([\d\.-]+)\s+([\d\.-]+)\).*?\(layer\s+"?Edge\.Cuts"?\)', content, re.DOTALL):
    print(f"Arc: ({m.group(1)}, {m.group(2)}) mid ({m.group(3)}, {m.group(4)}) -> ({m.group(5)}, {m.group(6)})")

# Let's find min and max X and Y of Edge.Cuts
pts = []
for m in re.finditer(r'\(gr_line\s+\(start\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(end\s+([\d\.-]+)\s+([\d\.-]+)\).*?\(layer\s+"?Edge\.Cuts"?\)', content, re.DOTALL):
    pts.append((float(m.group(1)), float(m.group(2))))
    pts.append((float(m.group(3)), float(m.group(4))))

if pts:
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    print(f"Main PCB X bounds: min={min(xs)}, max={max(xs)}, width={max(xs)-min(xs)}")
    print(f"Main PCB Y bounds: min={min(ys)}, max={max(ys)}, height={max(ys)-min(ys)}")

fps = []
for m in re.finditer(r'\(footprint\s+"([^"]+)".*?\(at\s+([\d\.-]+)\s+([\d\.-]+)(?:\s+([\d\.-]+))?\)', content, re.DOTALL):
    name = m.group(1)
    x = float(m.group(2))
    y = float(m.group(3))
    rot = m.group(4)
    fps.append((x, y, rot, name))
fps.sort(key=lambda t: t[0])
print("\n--- All Footprints sorted by X ---")
for x, y, rot, name in fps:
    print(f"{x:6.2f}, {y:6.2f} (rot={rot}) : {name}")



