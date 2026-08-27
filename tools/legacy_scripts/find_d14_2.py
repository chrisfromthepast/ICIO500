import re
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    content = f.read()

print('Searching for d14 tracks:')
for m in re.finditer(r'\(segment.*?\(net "d14"\)', content):
    print(m.group(0))

print('Searching for d14 pads:')
for m in re.finditer(r'\(pad.*?\n.*?\(net "d14"\)', content):
    print(m.group(0))
