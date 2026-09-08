import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

idx = pcb.find('Reference" "U5"')
start = pcb.rfind('(footprint', 0, idx)
end = pcb.find(')\n  )', idx) + 4
u5_text = pcb[start:end]

m_at = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?\)', u5_text)
u5_x = float(m_at.group(1))
u5_y = float(m_at.group(2))
u5_rot = float(m_at.group(3)) if m_at.group(3) else 0.0

import math
def rotate(px, py, angle):
    rad = math.radians(angle)
    qx = px * math.cos(rad) - py * math.sin(rad)
    qy = px * math.sin(rad) + py * math.cos(rad)
    return qx, qy

chunks = u5_text.split('(pad "')
for chunk in chunks[1:]:
    net_m = re.search(r'\(net\s+"([^"]+)"\)', chunk)
    if net_m:
        net = net_m.group(1)
        at_m = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)', chunk)
        if at_m:
            px = float(at_m.group(1))
            py = float(at_m.group(2))
            rx, ry = rotate(px, py, u5_rot)
            print(f"'{net}': ({u5_x + rx:.3f}, {u5_y + ry:.3f}),")
