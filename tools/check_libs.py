import re
with open('build/icio500/faceplate_logic.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()
print(set(re.findall(r'\(lib_id "([^"]+)"\)', text)))
