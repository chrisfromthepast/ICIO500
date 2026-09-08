import re

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Replace Satellite offset
pcb = pcb.replace('(xyz 0 166.675 119.05)', '(xyz 0 166.675 85.0)')

# Replace Faceplate offset
pcb = pcb.replace('(xyz -1.6 66.675 19.05)', '(xyz -1.6 66.675 -15.0)')

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)
