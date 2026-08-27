"""Find all vias and their nets, and locate the d14 net via specifically."""
import re

content = open('build/icio500/icio500.kicad_pcb', encoding='utf-8').read()

# Find all vias - parse each one properly
via_blocks = []
for m in re.finditer(r'\t\(via\n', content):
    start = m.start()
    depth = 0
    end = start
    for i in range(start, min(start + 500, len(content))):
        if content[i] == '(': depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                end = i
                break
    via_blocks.append(content[start:end+1])

print(f'Total vias: {len(via_blocks)}')
for i, vb in enumerate(via_blocks):
    net_m = re.search(r'\(net "([^"]+)"\)', vb)
    at_m = re.search(r'\(at ([\d.\s-]+)\)', vb)
    uuid_m = re.search(r'\(uuid "([^"]+)"\)', vb)
    net = net_m.group(1) if net_m else '?'
    at = at_m.group(1).strip() if at_m else '?'
    uid = uuid_m.group(1) if uuid_m else '?'
    if net == 'd14' or 'dangling' in net.lower():
        print(f'  [POSSIBLE D14] Via {i}: net={net} at=({at}) uuid={uid}')
    # Show all vias
    print(f'  Via {i}: net={net} at=({at}) uuid={uid[:8]}...')
