import re
with open('build/icio500/faceplate_logic.kicad_sch', 'r', encoding='utf-8') as f:
    content = f.read()
refs = re.findall(r'\(property "Reference" "([^"]+)"', content)
print('faceplate_logic schematic components:', sorted(set(refs)))
