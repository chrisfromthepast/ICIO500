import re
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

matches = re.finditer(r'\((gr_[a-z]+)[\s\S]*?\(layer "Edge\.Cuts"\)', text)
for m in matches:
    print(m.group(0))
