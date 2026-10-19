import math

# DIP-40 dimensions:
# 40 pins, 2 rows of 20 pins, 2.54mm pitch between pins, 15.24mm (600mil) between rows.
# In local footprint coords (unrotated, rot=0):
# Row 1 (pins 1 to 20): usually along left side or right side?
# Let's check local coords of U5 in the footprint definition!

import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

idx = pcb.find('"Reference" "U5"')
start = pcb.rfind('(footprint ', 0, idx)
depth = 0
end = start
for i in range(start, len(pcb)):
    if pcb[i] == '(': depth += 1
    elif pcb[i] == ')':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
block = pcb[start:end]

pads = []
for pb in re.finditer(r'\(pad\s+"([^"]+)"[^\n]*\n\s*\(at\s+([-\d.]+)\s+([-\d.]+)[^\)]*\)[\s\S]*?\(net\s+"([^"]*)"\)', block):
    num = pb.group(1)
    px = float(pb.group(2))
    py = float(pb.group(3))
    net = pb.group(4)
    pads.append((int(num), px, py, net))

pads.sort(key=lambda x: x[0])
print("Sample U5 unrotated local pads:")
for p in [pads[0], pads[1], pads[19], pads[20], pads[39]]:
    print(f"  Pin {p[0]:2d}: local=({p[1]:6.2f}, {p[2]:6.2f}) net={p[3]}")
