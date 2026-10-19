import re
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()
idx = pcb.find('Reference" "U6"')
start = pcb.rfind('(footprint', 0, idx)
end = pcb.find(')\n  )', idx) + 4
u6 = pcb[start:end]
for line in u6.split('\n'):
    if '(pad' in line or '(at' in line:
        print(line)
