import re

def create_final_pcb(src_pcb, dst_pcb):
    with open(src_pcb, 'r', encoding='utf-8') as f:
        content = f.read()

    DY = 11.43  # exactly 4.5 pin pitches (4.5 * 2.54 = 11.43 mm)
    
    # 1. Update U6 footprint position to (at 59.22 131.905 180)
    idx = content.find('(property "Reference" "U6"')
    fp_start = content.rfind('(footprint', 0, idx)
    fp_end = content.find('\n\t(footprint', idx)
    u6_block = content[fp_start:fp_end]
    
    u6_new = re.sub(r'\(at\s+[\d\.-]+\s+[\d\.-]+\s+180\)', '(at 59.22 131.905 180)', u6_block, count=1)
    content = content[:fp_start] + u6_new + content[fp_end:]
    
    # 2. Update Edge.Cuts - Top edge to 45.70, keeping bottom edge at 160.00
    content = content.replace('(start 55.39 55)\n\t\t(end 195 55)', '(start 55.39 45.7)\n\t\t(end 195 45.7)')
    content = content.replace('(start 55.39 160)\n\t\t(end 55.39 55)', '(start 55.39 160)\n\t\t(end 55.39 45.7)')
    content = content.replace('(start 195 55)\n\t\t(end 195 71.5)', '(start 195 45.7)\n\t\t(end 195 71.5)')
    
    # 3. Update ground zones
    content = content.replace('(xy 51.125 55.475) (xy 202.525 55.475)', '(xy 51.125 45.7) (xy 202.525 45.7)')
    content = content.replace('(xy 49.625 53.975) (xy 204.025 53.975)', '(xy 49.625 44.0) (xy 204.025 44.0)')
    
    # 4. Shift U6 routing elements
    u6_nets = {
        'daisy_5v_power', 'audio_in_r', 'gnd', 'i2c1_sda', 'i2c1_scl',
        'd13', 'd14', 'gpio_enc_b', 'gpio_enc_sw', 'spi1_mosi',
        'spi1_miso', 'spi1_sck', 'spi1_cs', 'gpio_disp_dc', 'gpio_disp_res'
    }
    
    lines = content.splitlines()
    out_lines = []
    curr = []
    in_item = False
    brace = 0
    
    for line in lines:
        if line.strip().startswith('(segment') or line.strip().startswith('(via'):
            in_item = True
            curr = [line]
            brace = line.count('(') - line.count(')')
        elif in_item:
            curr.append(line)
            brace += line.count('(') - line.count(')')
            if brace == 0:
                item_str = '\n'.join(curr)
                is_u6_net = any(f'"{net}"' in item_str for net in u6_nets)
                
                if is_u6_net:
                    via_m = re.search(r'\(via\s+.*?\(at\s+([-\d.]+)\s+([-\d.]+)\)', item_str, re.DOTALL)
                    seg_m = re.search(r'\(segment\s+.*?\(start\s+([-\d.]+)\s+([-\d.]+)\)\s+\(end\s+([-\d.]+)\s+([-\d.]+)\)', item_str, re.DOTALL)
                    
                    if via_m:
                        vx, vy = float(via_m.group(1)), float(via_m.group(2))
                        # Don't shift the fixed via for audio_in_r at (73, 118.5)
                        if 60 <= vx <= 75 and 100 <= vy <= 122 and not (abs(vx - 73.0) < 0.1 and abs(vy - 118.5) < 0.1):
                            new_vy = round(vy + DY, 3)
                            item_str = re.sub(r'\(at\s+([-\d.]+)\s+([-\d.]+)\)', f'(at {vx} {new_vy})', item_str)
                    elif seg_m:
                        x1, y1, x2, y2 = [float(g) for g in seg_m.groups()]
                        # Horizontal segment: y1 == y2 (within 0.1 mm) and in [95, 125]
                        if 55 <= min(x1, x2) and max(x1, x2) <= 75 and abs(y1 - y2) < 0.1 and 98 <= y1 <= 122:
                            new_y = round(y1 + DY, 3)
                            item_str = re.sub(r'\(start\s+([-\d.]+)\s+([-\d.]+)\)\s+\(end\s+([-\d.]+)\s+([-\d.]+)\)',
                                             f'(start {x1} {new_y}) (end {x2} {new_y})', item_str)
                        # Short vertical stub from U6 pad: x1 == x2 == 56.68, y in [100, 122]
                        elif abs(x1 - x2) < 0.1 and abs(x1 - 56.68) < 0.1 and 98 <= min(y1, y2) and max(y1, y2) <= 122:
                            new_y1 = round(y1 + DY, 3)
                            new_y2 = round(y2 + DY, 3)
                            item_str = re.sub(r'\(start\s+([-\d.]+)\s+([-\d.]+)\)\s+\(end\s+([-\d.]+)\s+([-\d.]+)\)',
                                             f'(start {x1} {new_y1}) (end {x2} {new_y2})', item_str)
                        # Vertical trace on In2.Cu: runs from via at Y in [100, 122] up to Y in [75, 86]
                        elif abs(x1 - x2) < 0.1 and 61 <= x1 <= 72 and 'In2.Cu' in item_str and 98 <= max(y1, y2) <= 122:
                            if y1 > y2:
                                new_y1 = round(y1 + DY, 3)
                                item_str = re.sub(r'\(start\s+([-\d.]+)\s+([-\d.]+)\)', f'(start {x1} {new_y1})', item_str)
                            else:
                                new_y2 = round(y2 + DY, 3)
                                item_str = re.sub(r'\(end\s+([-\d.]+)\s+([-\d.]+)\)', f'(end {x2} {new_y2})', item_str)
                        # Audio_in_r vertical stub on In2.Cu at X=73: from 121.745 to 118.5
                        elif abs(x1 - x2) < 0.1 and abs(x1 - 73.0) < 0.1 and 'In2.Cu' in item_str:
                            new_y1 = round(y1 + DY, 3)
                            item_str = re.sub(r'\(start\s+([-\d.]+)\s+([-\d.]+)\)', f'(start {x1} {new_y1})', item_str)
                        # Daisy 5V stub at X=74: from 120.475 to 120.5
                        elif abs(x1 - x2) < 0.1 and abs(x1 - 74.0) < 0.1:
                            new_y1 = round(y1 + DY, 3)
                            item_str = re.sub(r'\(start\s+([-\d.]+)\s+([-\d.]+)\)', f'(start {x1} {new_y1})', item_str)
                            
                out_lines.append(item_str)
                in_item = False
        else:
            out_lines.append(line)
            
    with open(dst_pcb, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out_lines))
        
    print(f"Applied all shifts successfully! Wrote {dst_pcb}")

create_final_pcb('build/icio500/icio500.kicad_pcb', 'build/icio500/test_final_main.kicad_pcb')
