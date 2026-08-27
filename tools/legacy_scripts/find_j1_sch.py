import re
with open('build/icio500/faceplate_logic.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()
j1_match = re.search(r'\(symbol\s+\(lib_id "Local:JST_SH_8".*?\(property "Reference" "J1".*?\n  \)', text, re.DOTALL)
if j1_match:
    print(j1_match.group(0))
else:
    print("J1 not found")
