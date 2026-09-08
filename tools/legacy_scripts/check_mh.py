import re
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f: pcb = f.read()
for m in re.findall(r'\(footprint "MountingHole:MountingHole.*?\(at [0-9.-]+ [0-9.-]+\)', pcb): print(m)
