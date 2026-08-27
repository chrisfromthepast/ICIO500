import re
with open('build/icio500/faceplate_logic.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()
labels = set(re.findall(r'\(net_label "([^"]+)"', text))
print('Net labels in sch:', sorted(labels))
