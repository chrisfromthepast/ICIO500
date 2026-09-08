import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

segments = re.findall(r'\(\s*segment\s*\n\s*\(\s*start\s+([\d\.]+)\s+([\d\.]+)\s*\)\s*\n\s*\(\s*end\s+([\d\.]+)\s+([\d\.]+)\s*\)\s*\n\s*\(\s*width\s+([\d\.]+)\s*\)\s*\n\s*\(\s*layer\s+"(.*?)"\s*\)\s*\n\s*\(\s*net\s+(.*?)\s*\)', pcb, re.DOTALL)

print(f"Total segments: {len(segments)}")

for sx, sy, ex, ey, w, l, n in segments:
    sx = float(sx)
    ex = float(ex)
    sy = float(sy)
    ey = float(ey)
    if (abs(sx - 52.17) < 0.2 or abs(ex - 52.17) < 0.2) and 100 < sy < 145:
        print(f"Trace {n} on {l} connected to ~52.17. Ends: {sx} to {ex}")
    if (abs(sx - 49.63) < 0.2 or abs(ex - 49.63) < 0.2) and 100 < sy < 145:
        print(f"Trace {n} on {l} connected to ~49.63. Ends: {sx} to {ex}")

