import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

segments = re.findall(r'\(\s*segment\s*\n\s*\(\s*start\s+([\d\.]+)\s+([\d\.]+)\s*\)\s*\n\s*\(\s*end\s+([\d\.]+)\s+([\d\.]+)\s*\)\s*\n\s*\(\s*width\s+([\d\.]+)\s*\)\s*\n\s*\(\s*layer\s+"(.*?)"\s*\)\s*\n\s*\(\s*net\s+(.*?)\s*\)', pcb, re.DOTALL)

ext = []
for sx, sy, ex, ey, w, l, n in segments:
    sx = float(sx)
    ex = float(ex)
    if (abs(sx - 56.0) < 0.1) or (abs(ex - 56.0) < 0.1):
        ext.append(l)

print(f"Segments starting/ending at ~56.0 (the new U6 position): {len(ext)}")
from collections import Counter
print(Counter(ext))
