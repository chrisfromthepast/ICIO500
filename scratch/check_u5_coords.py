import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('"Reference" "U5"')
start = c.rfind('(footprint', 0, idx)
depth = 0
end = start
for i in range(start, len(c)):
    if c[i] == '(': depth += 1
    elif c[i] == ')':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
block = c[start:end]

pads = []
for pm in re.finditer(r'\(pad\s+"(\d+)"[^\n]*\n\s*\(at\s+([-\d.]+)\s+([-\d.]+)', block):
    num = int(pm.group(1))
    lx = float(pm.group(2))
    ly = float(pm.group(3))
    # footprint at 130.92 112.51 -90
    # In KiCad, rotation theta in degrees (CW in standard screen coords, CCW in math):
    # dx = lx*cos(t) - ly*sin(t)
    # dy = lx*sin(t) + ly*cos(t)
    import math
    rad = math.radians(-90)
    ax = 130.92 + (lx * math.cos(rad) - ly * math.sin(rad))
    ay = 112.51 + (lx * math.sin(rad) + ly * math.cos(rad))
    pads.append((num, ax, ay, lx, ly))

pads.sort(key=lambda x: x[0])
print(f"Current U5 pads at (130.92, 112.51, rot=-90):")
print("\nSilkscreen boxes:")
for m in re.finditer(r'\(gr_text\s+"DIGITAL"[\s\S]*?\(at\s+([-\d.]+)\s+([-\d.]+)', c):
    print(f"DIGITAL text at ({m.group(1)}, {m.group(2)})")
for m in re.finditer(r'\(gr_rect\s+\(start\s+([-\d.]+)\s+([-\d.]+)\)\s+\(end\s+([-\d.]+)\s+([-\d.]+)\)[\s\S]*?\(layer\s+"F\.SilkS"\)', c):
    print(f"Silk rect: ({m.group(1)}, {m.group(2)}) -> ({m.group(3)}, {m.group(4)})")

