import re

with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Check net declarations
net_decls = re.findall(r'\(net (\d+) "([^"]+)"\)', pcb)
print(f"Net declarations: {len(net_decls)}")
for nid, name in sorted(net_decls, key=lambda x: int(x[0])):
    print(f"  {nid}: {name}")

# Check pad assignments by component
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

print("\nPad net assignments:")
for fp_match in re.finditer(r'\t\(footprint "', pcb):
    fp_start = fp_match.start()
    fp_end = find_end(pcb, fp_start)
    fp_block = pcb[fp_start:fp_end+1]
    
    ref_match = re.search(r'\(property "Reference" "([^"]+)"', fp_block)
    ref = ref_match.group(1) if ref_match else "?"
    
    pad_nets = re.findall(r'\(pad "([^"]+)".*?\(net (\d+) "([^"]+)"\)', fp_block, re.DOTALL)
    pads_total = len(re.findall(r'\(pad "', fp_block))
    pads_with_net = len(pad_nets)
    
    print(f"  {ref}: {pads_with_net}/{pads_total} pads netted")
    for pn, nid, nn in pad_nets:
        print(f"    pad {pn} -> {nn}")
