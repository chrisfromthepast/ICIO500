import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

j1_match = re.search(r'\(footprint "Connector_PinHeader_2.54mm:PinHeader_2x10.*?\(at ([0-9.-]+) ([0-9.-]+)', pcb, re.DOTALL)
if j1_match:
    print(f"J1 is at {j1_match.group(1)}, {j1_match.group(2)}")
else:
    print("J1 not found!")

j1_nets = set()
for match in re.finditer(r'\(pad "(\d+)" .*? \(net \d+ "([^"]+)"\)', j1_match.group(0)):
    print(f"Pad {match.group(1)} is on net {match.group(2)}")
    j1_nets.add(match.group(2))

# Find segments for these nets
segments = 0
for match in re.finditer(r'\(segment .*? \(net \d+ "([^"]+)"\)', pcb):
    if match.group(1) in j1_nets:
        segments += 1
print(f"Found {segments} segments for J1 nets")
