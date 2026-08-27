import re
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    content = f.read()

print('Searching for d14 tracks:')
for m in re.finditer(r'\(segment.*?\(net \d+\)', content):
    # wait, kicad 10 uses integer net IDs in segments!
    pass

# let's just find the net ID for d14
net_match = re.search(r'\(net (\d+) "d14"\)', content)
if net_match:
    net_id = net_match.group(1)
    print(f'd14 is net {net_id}')
    for m in re.finditer(r'\(segment.*?\(net ' + net_id + r'\)', content):
        print(m.group(0))
else:
    print('d14 net not found')
