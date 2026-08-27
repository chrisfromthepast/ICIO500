"""
Fix LED and encoder pad names and inject their nets.
LED 0805 footprint uses pads "1" (anode) and "2" (cathode)
Alps EC11E encoder uses pads A, B, C (encoder), S1, S2 (switch), MP (mounting)
"""
import re

# Correct mappings for actual pad names in the footprints
COMP_PIN_NET_FIX = {
    # D1-D10: LED_0805 pads are "1"=anode, "2"=cathode
    'D1':  {'1': 'GND', '2': 'LED_1_MID'},
    'D2':  {'1': 'GND', '2': 'LED_2_MID'},
    'D3':  {'1': 'GND', '2': 'LED_3_MID'},
    'D4':  {'1': 'GND', '2': 'LED_4_MID'},
    'D5':  {'1': 'GND', '2': 'LED_5_MID'},
    'D6':  {'1': 'GND', '2': 'LED_6_MID'},
    'D7':  {'1': 'GND', '2': 'LED_7_MID'},
    'D8':  {'1': 'GND', '2': 'LED_8_MID'},
    'D9':  {'1': 'GND', '2': 'LED_9_MID'},
    'D10': {'1': 'GND', '2': 'LED_10_MID'},
    # ENC1: Alps EC11E encoder
    # A = encoder channel A, B = encoder channel B, C = common (GND)
    # S1 = switch, S2 = switch common (GND)
    'ENC1': {
        'A': 'ENC_A',
        'B': 'ENC_B',
        'C': 'GND',
        'S1': 'ENC_SW',
        'S2': 'GND',
    },
}

# Net ID map (must match what inject_nets.py used)
NET_NAMES = sorted([
    "+3V3", "+3V3_IN", "ENC_A", "ENC_B", "ENC_SW", "GND",
    "LED_1", "LED_10", "LED_10_MID", "LED_1_MID",
    "LED_2", "LED_2_MID", "LED_3", "LED_3_MID",
    "LED_4", "LED_4_MID", "LED_5", "LED_5_MID",
    "LED_6", "LED_6_MID", "LED_7", "LED_7_MID",
    "LED_8", "LED_8_MID", "LED_9", "LED_9_MID",
    "SCL", "SDA",
])
net_id_map = {name: i+1 for i, name in enumerate(NET_NAMES)}

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

with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

for ref, pin_nets in COMP_PIN_NET_FIX.items():
    ref_pos = pcb.find(f'Reference" "{ref}"')
    if ref_pos == -1:
        print(f"WARNING: {ref} not found!")
        continue
    fp_start = pcb.rfind('\t(footprint ', 0, ref_pos)
    fp_end = find_end(pcb, fp_start)
    fp_block = pcb[fp_start:fp_end+1]
    
    for pin_num, net_name in pin_nets.items():
        nid = net_id_map[net_name]
        pad_pattern = f'(pad "{pin_num}" '
        pad_pos = fp_block.find(pad_pattern)
        if pad_pos == -1:
            print(f"WARNING: {ref} pad {pin_num} not found!")
            continue
        pad_end = find_end(fp_block, pad_pos)
        pad_text = fp_block[pad_pos:pad_end+1]
        
        if '(net ' in pad_text:
            pad_new = re.sub(r'\(net \d+ "[^"]*"\)', f'(net {nid} "{net_name}")', pad_text)
        else:
            pad_new = pad_text[:-1] + f' (net {nid} "{net_name}"))'
        
        fp_block = fp_block[:pad_pos] + pad_new + fp_block[pad_end+1:]
    
    pcb = pcb[:fp_start] + fp_block + pcb[fp_end+1:]
    print(f"  Fixed {ref}: {pin_nets}")

with open('build/icio500/panel_satellite.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)

print("\nDone! LED and encoder nets fixed.")
