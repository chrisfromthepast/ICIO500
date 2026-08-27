import re, math

pcb = open('build/icio500/icio500.kicad_pcb', encoding='utf-8').read()

fp_starts = [m.start() for m in re.finditer(r'\n\t\(footprint ', pcb)]

for idx in range(len(fp_starts)):
    start = fp_starts[idx]
    end = fp_starts[idx + 1] if idx + 1 < len(fp_starts) else len(pcb)
    fp_text = pcb[start:end]
    
    at_match = re.search(r'\n\t\t\(at ([\d.e-]+) ([\d.e-]+)(?: ([\d.e-]+))?\)', fp_text)
    if not at_match:
        continue
    fp_x = float(at_match.group(1))
    fp_y = float(at_match.group(2))
    fp_rot = float(at_match.group(3)) if at_match.group(3) else 0.0
    
    ref_match = re.search(r'"Reference" "([^"]+)"', fp_text)
    ref = ref_match.group(1) if ref_match else '??'
    
    print(f'=== {ref} at ({fp_x}, {fp_y}) rot={fp_rot} ===')
    
    rot_rad = math.radians(-fp_rot)
    cos_r = math.cos(rot_rad)
    sin_r = math.sin(rot_rad)
    
    # Find pads with nets
    pad_iter = re.finditer(
        r'\(pad "(\d+)"[^)]*\)\n\t\t\t\(at ([\d.e-]+) ([\d.e-]+)',
        fp_text
    )
    
    for pm in pad_iter:
        pad_num = pm.group(1)
        px = float(pm.group(2))
        py = float(pm.group(3))
        
        # Look ahead for net in this pad block
        pad_start = pm.start()
        # Find next pad or end of footprint
        next_pad = re.search(r'\(pad "', fp_text[pad_start + 10:])
        pad_end = pad_start + 10 + next_pad.start() if next_pad else len(fp_text)
        pad_block = fp_text[pad_start:pad_end]
        
        net_match = re.search(r'\(net "([^"]+)"\)', pad_block)
        net = net_match.group(1) if net_match else None
        
        abs_x = fp_x + px * cos_r - py * sin_r
        abs_y = fp_y + px * sin_r + py * cos_r
        
        if net:
            print(f'  pad {pad_num}: abs=({abs_x:.4f}, {abs_y:.4f}) net={net}')
