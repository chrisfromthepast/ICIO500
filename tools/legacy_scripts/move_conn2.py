import sys

# Read the PCB file
with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Move the connector from 133.0 161.5 to 105.0 178.0
import re
new_pcb = re.sub(r'\(at 133[.]?0? 161[.]?5? 90\)', '(at 105.0 178.0 90)', pcb)

with open('build/icio500/panel_satellite.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(new_pcb)
