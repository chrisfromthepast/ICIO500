import re
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

idx = pcb.find('Reference" "U6"')
start = pcb.rfind('(footprint', 0, idx)
end = pcb.find(')\n  )', idx) + 4
u6_text = pcb[start:end]

pads = re.findall(r'\(pad\s+"(\d+)".*?\(at\s+([\d.-]+)\s+([\d.-]+)\).*?\(net\s+"([^"]+)"\)', u6_text, re.DOTALL)
if not pads:
    pads = re.findall(r'\(pad\s+"(\d+)".*?\(at\s+([\d.-]+)\s+([\d.-]+)\)', u6_text, re.DOTALL)

for p in pads:
    print(f"Pad {p[0]} at {p[1]}, {p[2]}")
