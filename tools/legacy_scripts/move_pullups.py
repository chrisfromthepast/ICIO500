import sys
import re

with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Find R11 and R12 and change their positions
# They are currently at 125 114 and 131 114
# But wait, we need to know exactly which one is which, or we can just replace the strings!

pcb = re.sub(r'\(at 125[.]?0? 114[.]?0? 90\)', '(at 103.0 150.0 90)', pcb)
pcb = re.sub(r'\(at 131[.]?0? 114[.]?0? 90\)', '(at 103.0 153.0 90)', pcb)

with open('build/icio500/panel_satellite.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)
