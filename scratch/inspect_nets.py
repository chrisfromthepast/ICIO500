import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

def parse_fp(ref):
    idx = pcb.find(f'"Reference" "{ref}"')
    start = pcb.rfind('(footprint ', 0, idx)
    depth = 0
    end = start
    for i in range(start, len(pcb)):
        if pcb[i] == '(': depth += 1
        elif pcb[i] == ')':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    block = pcb[start:end]
    
    at_m = re.search(r'\(at ([-\d.]+) ([-\d.]+) ?([-\d.]*)\)', block)
    fx = float(at_m.group(1))
    fy = float(at_m.group(2))
    frot = float(at_m.group(3)) if at_m.group(3) else 0.0
    
    # parse pads: (pad "num" ... (at x y [rot]) ... (net "name"))
    pad_blocks = re.findall(r'\(pad\s+"([^"]+)"[\s\S]*?\n\t\t\)', block)
    pads = []
    for pb in re.finditer(r'\(pad\s+"([^"]+)"[^\n]*\n\s*\(at\s+([-\d.]+)\s+([-\d.]+)[^\)]*\)[\s\S]*?\(net\s+"([^"]*)"\)', block):
        num = pb.group(1)
        px = float(pb.group(2))
        py = float(pb.group(3))
        net = pb.group(4)
        pads.append((num, px, py, net))
    return fx, fy, frot, pads

fx6, fy6, rot6, pads6 = parse_fp('U6')
fx5, fy5, rot5, pads5 = parse_fp('U5')

print(f"U6: at ({fx6}, {fy6}), rot {rot6}")
for p in sorted(pads6, key=lambda x: int(x[0]) if x[0].isdigit() else 999):
    print(f"  Pin {p[0]:2s}: local=({p[1]:6.2f}, {p[2]:6.2f}) net='{p[3]}'")

print(f"\nU5: at ({fx5}, {fy5}), rot {rot5}")
u6_nets = {p[3] for p in pads6 if p[3]}
for p in sorted(pads5, key=lambda x: int(x[0]) if x[0].isdigit() else 999):
    shared = f" <== CONNECTED TO U6 Pin {[x[0] for x in pads6 if x[3]==p[3]]}" if p[3] in u6_nets and p[3] not in ['gnd', ''] else ""
    print(f"  Pin {p[0]:2s}: local=({p[1]:6.2f}, {p[2]:6.2f}) net='{p[3]}'{shared}")
