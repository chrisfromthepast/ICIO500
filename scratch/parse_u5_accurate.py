import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('"Reference" "U5"')
start = c.rfind('(footprint', 0, idx)
depth = 0
end = start
for i in range(start, len(c)):
    if c[i] == '(': depth += 1
    elif c[i] == ')':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
block = c[start:end]

# Split by "(pad "
pad_chunks = block.split('(pad ')
print(f"Total pad chunks: {len(pad_chunks)-1}")
for chunk in pad_chunks[1:]:
    # first token is pad number
    m = re.match(r'"([^"]+)"\s+(\w+)\s+(\w+)\s*\(at\s+([-\d.]+)\s+([-\d.]+)', chunk)
    if m:
        num = m.group(1)
        ptype = m.group(2)
        pshape = m.group(3)
        lx = float(m.group(4))
        ly = float(m.group(5))
        net_m = re.search(r'\(net\s+"([^"]*)"\)', chunk)
        net = net_m.group(1) if net_m else ""
        if net:
            print(f"  Pad {num:2s}: local=({lx:6.2f}, {ly:6.2f}) net='{net}'")
