import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Replace U6 position
# The old position was (at 93.37 107 90)
pcb = re.sub(r'\(at 93.37 107 90\)', '(at 93.37 123.475 90)', pcb)

with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)
