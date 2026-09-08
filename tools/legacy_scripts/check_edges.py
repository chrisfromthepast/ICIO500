import re
with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

lines = pcb.split('\n')
for i, line in enumerate(lines):
    if '"Edge.Cuts"' in line and 'gr_' in lines[i-3]:
        print(lines[i-3].strip())
        print(lines[i-2].strip())
        print(lines[i-1].strip())
