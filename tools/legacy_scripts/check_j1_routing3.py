import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

j1_nets = set()
in_j1 = False
for line in pcb.split('\n'):
    if 'footprint "Connector_PinHeader_2.54mm:PinHeader_2x10' in line:
        in_j1 = True
    if in_j1 and '(pad' in line:
        match = re.search(r'\(net \d+ "([^"]+)"\)', line)
        if match:
            j1_nets.add(match.group(1))
            print(f"J1 pad net: {match.group(1)}")
    if in_j1 and ')' == line.strip(): # Very rough
        pass # whatever
    if in_j1 and '(model' in line:
        in_j1 = False

segments = 0
for match in re.finditer(r'\(segment .*?\(net (\d+) "([^"]+)"\)', pcb):
    if match.group(2) in j1_nets:
        segments += 1
print(f"Found {segments} segments for J1 nets")
