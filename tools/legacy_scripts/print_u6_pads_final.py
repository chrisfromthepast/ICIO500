import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    lines = f.readlines()

u6_start = -1
for i, line in enumerate(lines):
    if 'Reference" "U6"' in line:
        for j in range(i, 0, -1):
            if '(footprint' in lines[j]:
                u6_start = j
                break
        break

for j in range(u6_start, u6_start+150):
    if '(pad "' in lines[j]:
        print(lines[j].strip())
