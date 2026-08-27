import re
with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()
for m in re.finditer(r'\(footprint "([^"]+)".*?\(property "Reference" "([^"]+)".*?\(at ([\d.-]+) ([\d.-]+)(?: ([\d.-]+))?\)', text, re.DOTALL):
    print(f"{m.group(2)} ({m.group(1)}): X={m.group(3)}, Y={m.group(4)}, Rot={m.group(5)}")
