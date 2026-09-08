import re
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f: pcb = f.read()
for m in re.findall(r'\(gr_line[\s\S]*?\(layer "Edge\.Cuts"\)[\s\S]*?\n\t\)', pcb)[:5]: print(m)
