import re

pcb = open('build/icio500/icio500.kicad_pcb', encoding='utf-8').read()

TARGET_X, TARGET_Y = 159.5, 78.0
TOL = 0.05

print('Segments touching (159.5, 78.0):')
for m in re.finditer(
    r'\(segment\s+\(start ([\d.]+) ([\d.]+)\)\s+\(end ([\d.]+) ([\d.]+)\)\s+\(width ([\d.]+)\)\s+\(layer "([^"]+)"\)\s+\(net "([^"]+)"\)',
    pcb
):
    sx, sy = float(m.group(1)), float(m.group(2))
    ex, ey = float(m.group(3)), float(m.group(4))
    net = m.group(7)
    layer = m.group(6)
    for x, y in [(sx, sy), (ex, ey)]:
        if abs(x - TARGET_X) < TOL and abs(y - TARGET_Y) < TOL:
            print(f'  [{net}] ({sx},{sy}) -> ({ex},{ey}) on {layer}')
            break
