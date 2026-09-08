import re
import uuid

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# 1. Move U6 to 56.0
pcb = re.sub(r'\(at 52\.17 103\.825 180\)', r'(at 56.0 103.825 180)', pcb)

# 2. Extract U6 block
u6_match = re.search(r'\(footprint "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Horizontal".*?Reference" "U6".*?\n  \)', pcb, re.DOTALL)
if not u6_match:
    # Try a looser match
    u6_match = re.search(r'\(footprint.*?Reference" "U6".*?(?:\n  \))', pcb, re.DOTALL)

if u6_match:
    u6_text = u6_match.group(0)
    # Find all pads
    pads = re.findall(r'\(pad "(\d+)" .*?\(at (.*?) (.*?)(?: |\)).*?\(net (\d+) "(.*?)"\)', u6_text)
    
    segments = []
    for pin, px_rel, py_rel, net_code, net_name in pads:
        px_rel = float(px_rel)
        py_rel = float(py_rel)
        
        # U6 is at 56.0 103.825, rotated 180
        # Absolute coordinates:
        # X_abs = 56.0 - px_rel
        # Y_abs = 103.825 - py_rel
        px_abs = 56.0 - px_rel
        py_abs = 103.825 - py_rel
        
        # The old pad was at X_abs - 3.83
        px_old = px_abs - 3.83
        
        width = 0.4 if net_name in ['gnd', 'GND', 'v_plus', 'v_minus', 'daisy_5v_power', '+3V3', '+3V3_IN'] else 0.25
        uid = str(uuid.uuid4())
        
        seg = f'\n  (segment (start {px_old:.4f} {py_abs:.4f}) (end {px_abs:.4f} {py_abs:.4f}) (width {width}) (layer "F.Cu") (net {net_code}) (uuid "{uid}"))'
        segments.append(seg)
    
    insert_pos = pcb.rfind('\n)')
    pcb = pcb[:insert_pos] + ''.join(segments) + pcb[insert_pos:]
    
    with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
        f.write(pcb)
    print(f"Moved U6 and appended {len(segments)} segments!")
else:
    print("U6 not found in text!")
