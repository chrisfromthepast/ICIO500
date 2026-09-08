import re
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'\(property "Reference" "U6"\s+\(at ([\d\.-]+) ([\d\.-]+)', text)
if m:
    print(f"U6 is at X={m.group(1)}, Y={m.group(2)}")
else:
    print("U6 not found!")
