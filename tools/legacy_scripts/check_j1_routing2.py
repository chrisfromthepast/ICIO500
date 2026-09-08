import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

fps = re.findall(r'\(footprint "Connector_PinHeader_2.54mm:PinHeader_2x10.*?(?=\n  \()', pcb, re.DOTALL)
if fps:
    j1_fp = fps[0]
    j1_nets = set()
    for match in re.finditer(r'\(pad "(\d+)" .*? \(net \d+ "([^"]+)"\)', j1_fp):
        print(f"Pad {match.group(1)} is on net {match.group(2)}")
        j1_nets.add(match.group(2))
    
    segments = 0
    for match in re.finditer(r'\(segment .*? \(net \d+ "([^"]+)"\)', pcb):
        if match.group(1) in j1_nets:
            segments += 1
    print(f"Found {segments} segments for J1 nets")
else:
    print("J1 not found!")
