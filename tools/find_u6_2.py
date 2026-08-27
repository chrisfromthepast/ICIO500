import re
with open('build/icio500/icio500.kicad_sch', 'r', encoding='utf-8') as f:
    content = f.read()

symbols = re.finditer(r'\(symbol \(lib_id "([^"]+)".*?\(property "Reference" "([^"]+)"', content, re.DOTALL)
for m in symbols:
    if m.group(2) == 'U6':
        print(f"U6 is a {m.group(1)}")
