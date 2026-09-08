import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

nets = re.findall(r'\(net\s+\d+\s+"([^"]+)"\)', pcb)
nets = list(set(nets))
nets.sort()
for n in nets:
    print(n)
