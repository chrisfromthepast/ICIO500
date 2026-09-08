with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

import re

# Find U6 footprint and replace its X coordinate
# (at 52.17 103.825 180)
pcb = re.sub(r'\(at 52\.17 103\.825 180\)', r'(at 56.0 103.825 180)', pcb)

with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)
print("Moved U6 to X=56.0")
