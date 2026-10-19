import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    c = f.read()

# search for "U5" in reference or Package_DIP
start_idx = c.find('DIP-40_W15.24mm_Socket')
if start_idx != -1:
    # backtrack to '(footprint'
    fp_start = c.rfind('(footprint', 0, start_idx)
    # find matching closing paren
    count = 0
    fp_end = fp_start
    for i in range(fp_start, len(c)):
        if c[i] == '(':
            count += 1
        elif c[i] == ')':
            count -= 1
            if count == 0:
                fp_end = i + 1
                break
    fp_text = c[fp_start:fp_end]
    print(f"Found U5 footprint! Length={len(fp_text)}")
    for pm in re.finditer(r'\(pad\s+"(\d+)"\s+thru_hole\s+([^\s]+)\s+\(at\s+([\d\.-]+)\s+([\d\.-]+)\).*?\(net\s+(\d+)\s+"([^"]*)"\)', fp_text, re.DOTALL):
        pad_num = int(pm.group(1))
        pad_type = pm.group(2)
        px = float(pm.group(3))
        py = float(pm.group(4))
        net_id = int(pm.group(5))
        net_name = pm.group(6)
        if net_name:
            print(f"  Pad {pad_num:2d}: local=({px:6.2f}, {py:6.2f}) -> net {net_id}: {net_name}")
