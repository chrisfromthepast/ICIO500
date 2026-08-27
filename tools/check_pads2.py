import re

with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

def find_end(content, start):
    depth = 0
    for i in range(start, len(content)):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    return -1

# Check what pads exist for D1, ENC1
for ref in ['D1', 'D2', 'ENC1']:
    ref_pos = pcb.find(f'Reference" "{ref}"')
    if ref_pos == -1:
        print(f"{ref}: NOT FOUND")
        continue
    fp_start = pcb.rfind('\t(footprint ', 0, ref_pos)
    fp_end = find_end(pcb, fp_start)
    fp_block = pcb[fp_start:fp_end+1]
    
    # Find all pad numbers
    pads = re.findall(r'\(pad "([^"]+)"', fp_block)
    # Check for net assignments
    nets = re.findall(r'\(net \d+ "([^"]+)"\)', fp_block)
    print(f"{ref}: pads={pads}, nets={nets}")
