import re

with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    content = f.read()

# find J1 footprint
fp_matches = re.finditer(r'\(footprint "[^"]+"', content)
for m in fp_matches:
    start = m.start()
    depth = 0
    end = start
    for i in range(start, len(content)):
        if content[i] == '(': depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                end = i
                break
    fp_block = content[start:end+1]
    if 'Reference" "J1"' in fp_block:
        print("Found J1. Pads:")
        for pad_m in re.finditer(r'\(pad "([^"]+)" .*?\(net \d+ "([^"]+)"\)', fp_block):
            print(f"  Pad {pad_m.group(1)}: {pad_m.group(2)}")
