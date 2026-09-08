import re

# Update satellite connector
with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

pcb = re.sub(r'\(at 105[.]?0? 178[.]?0? 90\)', '(at 105 175 0)', pcb)

with open('build/icio500/panel_satellite.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)

# Update main connector
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

pcb = re.sub(r'\(at 93.37 123.475 90\)', '(at 93.37 123.475 0)', pcb)

with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)
