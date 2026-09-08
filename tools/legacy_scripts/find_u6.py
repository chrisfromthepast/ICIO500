import re
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'\(footprint "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical_SMD"[\s\S]*?\(property "Reference" "U6"[\s\S]*?\(at ([\d\.-]+) ([\d\.-]+)', text)
if m:
    print(f"U6 is at X={m.group(1)}, Y={m.group(2)}")
else:
    print("U6 not found!")
