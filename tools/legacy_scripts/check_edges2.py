import re
with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Find all shapes on Edge.Cuts
matches = re.finditer(r'\((gr_[a-z]+)[\s\S]*?\(layer "Edge\.Cuts"\)', text)
for m in matches:
    print(m.group(0))
