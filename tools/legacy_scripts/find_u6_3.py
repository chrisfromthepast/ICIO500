import re
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
for i, line in enumerate(lines):
    if 'property "Reference" "U6"' in line:
        print("\n".join(lines[i-15:i+15]))
        break
