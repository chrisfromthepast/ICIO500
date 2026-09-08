import re
with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()
m = re.search(r'PinSocket_2x10_P2\.54mm_Vertical_SMD.*?\n\s*\(layer\s+"([^"]+)"\)', pcb)
if m: print(f'J1 layer: {m.group(1)}')
