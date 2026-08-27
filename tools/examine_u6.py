"""Find U6 pad 7 in the PCB and examine its zone connection settings."""
import re

PCB = 'build/icio500/icio500.kicad_pcb'
content = open(PCB, encoding='utf-8').read()

# Find U6 reference
u6_pos = content.find('"U6"')
if u6_pos < 0:
    print('U6 not found')
    exit()

# Find enclosing footprint start
fp_start = content.rfind('\t(footprint', 0, u6_pos)
print(f'U6 footprint starts at pos {fp_start}, line ~{content[:fp_start].count(chr(10))+1}')

# Find footprint end
depth = 0
fp_end = fp_start
for i in range(fp_start, min(fp_start + 300000, len(content))):
    if content[i] == '(': depth += 1
    elif content[i] == ')':
        depth -= 1
        if depth == 0:
            fp_end = i
            break

fp_block = content[fp_start:fp_end+1]
print(f'U6 footprint: {len(fp_block)} chars')

# Find pad 7
pad7_matches = list(re.finditer(r'\t\t\(pad "7"', fp_block))
print(f'Found {len(pad7_matches)} pad(s) numbered "7"')

for m in pad7_matches:
    pad_start_in_fp = m.start()
    pad_abs = fp_start + pad_start_in_fp
    
    # Find pad block end
    depth = 0
    pad_end = pad_abs
    for i in range(pad_abs, min(pad_abs + 1000, len(content))):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                pad_end = i
                break
    
    pad_block = content[pad_abs:pad_end+1]
    print(f'\nPad 7 block ({pad_end-pad_abs+1} chars):')
    print(pad_block)
    print(f'Has zone_connect: {"zone_connect" in pad_block}')
    net_m = re.search(r'\(net "([^"]+)"\)', pad_block)
    print(f'Net: {net_m.group(1) if net_m else "?"}')

# Also check U6 footprint-level zone settings
print('\n--- Footprint-level zone settings ---')
for kw in ('zone_connect', 'thermal_width', 'thermal_gap'):
    if kw in fp_block:
        # Find context
        idx = fp_block.find(kw)
        print(f'{kw} at offset {idx}: {repr(fp_block[max(0,idx-20):idx+40])}')
    else:
        print(f'{kw}: not set')
