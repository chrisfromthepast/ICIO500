import re
with open('build/icio500/icio500.kicad_sch', 'r') as f:
    text = f.read()
symbols = re.findall(r'\(symbol "(.*?)"', text)
print("Symbols in schematic:")
for s in symbols:
    print(s)
