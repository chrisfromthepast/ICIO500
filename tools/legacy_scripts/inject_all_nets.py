"""
Complete net injection for panel_satellite.kicad_pcb.
Does everything in a single pass with proper offset tracking.
"""
import re
import uuid

# ---- NET DEFINITIONS ----
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

# ---- COMPONENT PIN -> NET MAPPING ----
COMP_PIN_NET = {
    'J1': {
        '1': '+3V3', '2': '+3V3', '3': 'GND', '4': 'SDA',
        '5': 'GND', '6': 'SCL', '7': 'GND', '8': 'ENC_A',
        '9': 'ENC_B', '10': 'ENC_SW',
    },
    'U1': {
        '1': '+3V3', '2': 'GND', '3': 'SDA', '4': 'SCL',
        '5': '+3V3', '6': 'GND',
        '7': 'LED_1', '8': 'LED_2', '9': 'LED_3', '10': 'LED_4',
        '11': 'LED_5', '12': 'LED_6', '13': 'LED_7', '14': 'LED_8',
        '15': 'LED_9', '16': 'LED_10',
    },
    'ENC1': {'A': 'ENC_A', 'B': 'ENC_B', 'C': 'GND', 'S1': 'ENC_SW', 'S2': 'GND'},
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
    'R1':  {'1': 'LED_1_MID', '2': 'LED_1'},
    'R2':  {'1': 'LED_2_MID', '2': 'LED_2'},
    'R3':  {'1': 'LED_3_MID', '2': 'LED_3'},
    'R4':  {'1': 'LED_4_MID', '2': 'LED_4'},
    'R5':  {'1': 'LED_5_MID', '2': 'LED_5'},
    'R6':  {'1': 'LED_6_MID', '2': 'LED_6'},
    'R7':  {'1': 'LED_7_MID', '2': 'LED_7'},
    'R8':  {'1': 'LED_8_MID', '2': 'LED_8'},
    'R9':  {'1': 'LED_9_MID', '2': 'LED_9'},
    'R10': {'1': 'LED_10_MID', '2': 'LED_10'},
    'R11': {'1': 'SDA', '2': '+3V3'},
    'R12': {'1': 'SCL', '2': '+3V3'},
    'C1':  {'1': '+3V3', '2': 'GND'},
    'C2':  {'1': '+3V3', '2': 'GND'},
    'FB1': {'1': '+3V3_IN', '2': '+3V3'},
}

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

# ---- READ PCB ----
with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# ---- STEP 1: Clean out any existing net declarations (except net 0) and re-inject ----
# Remove all existing non-zero net declarations
pcb = re.sub(r'\t\(net [1-9]\d* "[^"]*"\)\n', '', pcb)

# Build fresh net declaration block
net_decl_block = '\n'.join(f'\t(net {nid} "{name}")' for name, nid in sorted(net_id_map.items(), key=lambda x: x[1]))
pcb = pcb.replace('\t(net 0 "")\n', f'\t(net 0 "")\n{net_decl_block}\n')

# ---- STEP 2: Strip all existing net assignments from pads ----
pcb = re.sub(r' \(net \d+ "[^"]*"\)', '', pcb)
pcb = re.sub(r'\s*\(net "[^"]*"\)', '', pcb)

# ---- STEP 3: Process each footprint and add net assignments to pads ----
# We process footprints one at a time, working on isolated blocks
result_parts = []
last_end = 0

for fp_match in re.finditer(r'\t\(footprint "', pcb):
    fp_start = fp_match.start()
    fp_end = find_end(pcb, fp_start)
    
    # Copy everything before this footprint
    result_parts.append(pcb[last_end:fp_start])
    
    fp_block = pcb[fp_start:fp_end+1]
    
    ref_match = re.search(r'\(property "Reference" "([^"]+)"', fp_block)
    ref = ref_match.group(1) if ref_match else None
    
    if ref and ref in COMP_PIN_NET:
        pin_nets = COMP_PIN_NET[ref]
        for pin_num, net_name in pin_nets.items():
            nid = net_id_map[net_name]
            # Find each pad with this pin number
            pad_pattern = f'(pad "{pin_num}" '
            idx = 0
            while True:
                pad_pos = fp_block.find(pad_pattern, idx)
                if pad_pos == -1:
                    break
                pad_end = find_end(fp_block, pad_pos)
                pad_text = fp_block[pad_pos:pad_end+1]
                # Insert net before closing paren
                pad_new = pad_text[:-1] + f' (net {nid} "{net_name}"))'
                fp_block = fp_block[:pad_pos] + pad_new + fp_block[pad_end+1:]
                idx = pad_pos + len(pad_new)
        
        assigned = sum(1 for p in re.findall(r'\(net \d+', fp_block))
        print(f"  {ref}: {assigned} pads netted")
    
    result_parts.append(fp_block)
    last_end = fp_end + 1

# Append remainder
result_parts.append(pcb[last_end:])
pcb = ''.join(result_parts)

# ---- WRITE BACK ----
with open('build/icio500/panel_satellite.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)

# Verify balance
print(f"\nParentheses balance: {pcb.count('(') - pcb.count(')')}")
print("Done! All nets cleanly injected.")
