import re
import uuid

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

pcb = re.sub(r'\(at 52\.17 103\.825 180\)', r'(at 56.0 103.825 180)', pcb)

footprints = pcb.split('\n  (footprint ')
segments = []
for fp_text in footprints:
    if '"U6"' in fp_text and 'PinHeader' in fp_text:
        pads = re.findall(r'\(pad "(\d+)" .*?\(at (.*?) (.*?)(?: |\)).*?\(net (\d+) "(.*?)"\)', fp_text)
        
        for pin, px_rel, py_rel, net_code, net_name in pads:
            px_rel = float(px_rel)
            py_rel = float(py_rel)
            
            px_abs = 56.0 - px_rel
            py_abs = 103.825 - py_rel
            
            px_old = px_abs - 3.83
            
            width = 0.4 if net_name in ['gnd', 'GND', 'v_plus', 'v_minus', 'daisy_5v_power', '+3V3', '+3V3_IN'] else 0.25
            uid = str(uuid.uuid4())
            
            seg = f'\n  (segment (start {px_old:.4f} {py_abs:.4f}) (end {px_abs:.4f} {py_abs:.4f}) (width {width}) (layer "F.Cu") (net {net_code}) (uuid "{uid}"))'
            segments.append(seg)
        break

if segments:
    insert_pos = pcb.rfind('\n)')
    pcb = pcb[:insert_pos] + ''.join(segments) + pcb[insert_pos:]
    
    with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
        f.write(pcb)
    print(f"Moved U6 and appended {len(segments)} segments!")
else:
    print("Failed to find pads!")
