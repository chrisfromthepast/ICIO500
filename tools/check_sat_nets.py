import re
with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()
nets = set(re.findall(r'\(net \d+ "([^"]+)"\)', text))
print('Nets in satellite board:', sorted(nets))
