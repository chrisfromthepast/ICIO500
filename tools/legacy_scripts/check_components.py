import re
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

fps = re.findall(r'\(footprint\s+"([^"]+)".*?\(at\s+([\d.-]+)\s+([\d.-]+)', pcb, re.DOTALL)
for fp, x, y in fps:
    if 'Connector' in fp or 'Header' in fp:
        print(f'{fp} at {x}, {y}')
