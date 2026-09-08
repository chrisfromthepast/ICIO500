import re
with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

match = re.search(r'\(footprint "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical".*?\n\t\)', pcb, re.DOTALL)
if match:
    print("Found! Length:", len(match.group(0)))
else:
    print("Not found.")
