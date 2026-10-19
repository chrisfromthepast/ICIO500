import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    c = f.read()

for m in re.finditer(r'\(segment[\s\S]*?\(net\s+"v_minus"\)[\s\S]*?\)', c):
    print(m.group(0))
