with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

import re
pcb = re.sub(r'\(setup', r'(setup\n    (grid_origin 119.05 175.0)', pcb)

with open('build/icio500/panel_satellite.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)

print("Set grid origin in panel_satellite")
