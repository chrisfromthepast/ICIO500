"""Find the d14 dangling via and details around C19 pad 2."""
import re

pcb = open('build/icio500/icio500.kicad_pcb', encoding='utf-8').read()

# 1. Find the d14 dangling via at (102.49, 107.00)
print("=== d14 vias ===")
for m in re.finditer(
    r'\(via\s+\(at ([\d.]+) ([\d.]+)\)\s+\(size ([\d.]+)\)\s+\(drill ([\d.]+)\)\s+\(layers "([^"]+)" "([^"]+)"\)\s+\(net "([^"]+)"\)\s+\(uuid "([^"]+)"\)',
    pcb
):
    if m.group(7) == 'd14':
        print(f'  at=({m.group(1)}, {m.group(2)}) size={m.group(3)} drill={m.group(4)} uuid={m.group(8)}')

# Also find d14 segments
print("\n=== d14 segments ===")
for m in re.finditer(
    r'\(segment\s+\(start ([\d.]+) ([\d.]+)\)\s+\(end ([\d.]+) ([\d.]+)\)\s+\(width ([\d.]+)\)\s+\(layer "([^"]+)"\)\s+\(net "d14"\)',
    pcb
):
    print(f'  ({m.group(1)},{m.group(2)}) -> ({m.group(3)},{m.group(4)}) layer={m.group(6)}')

# 2. Find all GND segments/traces touching C19 pad 2 at (159.50, 78.00)
print("\n=== GND connections to C19 pad 2 at (159.50, 78.00) ===")
px, py = 159.50, 78.00
TOL = 0.1
for m in re.finditer(
    r'\(segment\s+\(start ([\d.]+) ([\d.]+)\)\s+\(end ([\d.]+) ([\d.]+)\)\s+\(width ([\d.]+)\)\s+\(layer "([^"]+)"\)\s+\(net "gnd"\)',
    pcb
):
    sx, sy = float(m.group(1)), float(m.group(2))
    ex, ey = float(m.group(3)), float(m.group(4))
    for x, y in [(sx, sy), (ex, ey)]:
        if abs(x - px) < TOL and abs(y - py) < TOL:
            print(f'  ({sx},{sy}) -> ({ex},{ey}) layer={m.group(6)} w={m.group(5)}')
            break

# Check what GND copper is near C19 pad 2
print("\n=== GND segments/vias within 5mm of C19 pad 2 ===")
for m in re.finditer(
    r'\(segment\s+\(start ([\d.]+) ([\d.]+)\)\s+\(end ([\d.]+) ([\d.]+)\)\s+\(width ([\d.]+)\)\s+\(layer "([^"]+)"\)\s+\(net "gnd"\)',
    pcb
):
    sx, sy = float(m.group(1)), float(m.group(2))
    ex, ey = float(m.group(3)), float(m.group(4))
    import math
    d1 = math.sqrt((sx-px)**2 + (sy-py)**2)
    d2 = math.sqrt((ex-px)**2 + (ey-py)**2)
    if min(d1, d2) < 5.0:
        print(f'  ({sx},{sy}) -> ({ex},{ey}) layer={m.group(6)} w={m.group(5)}')

print("\n=== GND vias within 5mm of C19 pad 2 ===")
import math
for m in re.finditer(
    r'\(via\s+\(at ([\d.]+) ([\d.]+)\)\s+\(size ([\d.]+)\).*?\(net "gnd"\)',
    pcb, re.DOTALL
):
    vx, vy = float(m.group(1)), float(m.group(2))
    d = math.sqrt((vx-px)**2 + (vy-py)**2)
    if d < 5.0:
        print(f'  via at ({vx},{vy}) size={m.group(3)} dist={d:.2f}mm')
