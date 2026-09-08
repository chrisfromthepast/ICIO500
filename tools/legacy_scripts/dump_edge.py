import re

with open('build/icio500/faceplate_front.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Find all gr_* that have (layer "Edge.Cuts")
matches = re.findall(r'(\(gr_[^\)]+[\s\S]*?\(layer "Edge\.Cuts"\)[\s\S]*?\n\t\))', pcb)
for m in matches:
    print(m)
