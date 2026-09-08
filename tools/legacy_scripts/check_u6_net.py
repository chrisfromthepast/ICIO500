import re
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

idx = pcb.find('Reference" "U6"')
start = pcb.rfind('(footprint', 0, idx)
end = pcb.find(')\n  )', idx) + 4
u6_text = pcb[start:end]

for p in u6_text.split('(pad "')[1:]:
    if p.startswith('19"'):
        m_net = re.search(r'\(net\s+"([^"]+)"\)', p)
        if m_net:
            print(f"Pad 19 net: {m_net.group(1)}")
