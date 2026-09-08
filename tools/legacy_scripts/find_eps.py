import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

segments = re.findall(r'\(segment \(start ([\d\.]+) ([\d\.]+)\) \(end ([\d\.]+) ([\d\.]+)\)', pcb)

print("Endpoints in zone X:[48-54], Y:[80-120]:")
for sx, sy, ex, ey in segments:
    sx, sy, ex, ey = float(sx), float(sy), float(ex), float(ey)
    if 48 < sx < 54 and 80 < sy < 120:
        print(f"sx={sx}, sy={sy}")
    if 48 < ex < 54 and 80 < ey < 120:
        print(f"ex={ex}, ey={ey}")
