import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# We need U5's pad coordinates.
idx = pcb.find('Reference" "U5"')
start = pcb.rfind('(footprint', 0, idx)
end = pcb.find(')\n  )', idx) + 4
u5_text = pcb[start:end]

pads = re.findall(r'\(pad\s+"(\d+)".*?\(at\s+([\d.-]+)\s+([\d.-]+)\)', u5_text)
# U5 might have rotation!
m_at = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?\)', u5_text)
u5_x, u5_y, u5_rot = 0.0, 0.0, 0.0
if m_at:
    u5_x = float(m_at.group(1))
    u5_y = float(m_at.group(2))
    if m_at.group(3):
        u5_rot = float(m_at.group(3))

print(f"U5 at {u5_x}, {u5_y}, rot {u5_rot}")

import math
def rotate(px, py, angle):
    rad = math.radians(angle)
    qx = px * math.cos(rad) - py * math.sin(rad)
    qy = px * math.sin(rad) + py * math.cos(rad)
    return qx, qy

for p in pads:
    px = float(p[1])
    py = float(p[2])
    rx, ry = rotate(px, py, u5_rot)
    final_x = u5_x + rx
    final_y = u5_y + ry
    print(f"U5 Pad {p[0]}: {final_x}, {final_y}")
