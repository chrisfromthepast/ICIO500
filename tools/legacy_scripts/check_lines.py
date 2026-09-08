import re
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

m = re.search(r'(PinHeader_2x10_P2\.54mm_Horizontal.*?)\n\s*\(pad', pcb, re.DOTALL)
if m:
    print(m.group(1))
