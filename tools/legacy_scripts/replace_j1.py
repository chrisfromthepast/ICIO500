import re
import uuid

def balance(s): return s.count('(') - s.count(')')

def find_end(content, start):
    depth = 0
    for i in range(start, len(content)):
        if content[i] == '(': depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0: return i
    return -1

# 1. Read U6 from main board
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    main_pcb = f.read()

U6_PAD7_UUID = 'e444e20b-db2b-4839-8f41-e674ee2fa850'
u6_pad_pos = main_pcb.find(U6_PAD7_UUID)
u6_start = main_pcb.rfind('\t(footprint ', 0, u6_pad_pos)
u6_end = find_end(main_pcb, u6_start)
u6_block = main_pcb[u6_start:u6_end+1]

# Make U6 a clean J1
# Remove all nets from the pads because the satellite board has different net IDs!
u6_block = re.sub(r'\s*\(net \d+ "[^"]+"\)', '', u6_block)
# Replace Reference U6 with J1
u6_block = re.sub(r'\(property "Reference" "U6"', '(property "Reference" "J1"', u6_block)
# Replace the old position
u6_block = re.sub(r'\(at 93\.37 107(?:\.0+)? 90\)', '(at 119.05 103.50 90)', u6_block)

# Generate new UUIDs so we don't conflict with main board!
def replace_uuid(m):
    return f'(uuid "{uuid.uuid4()}")'
u6_block = re.sub(r'\(uuid "[^"]+"\)', replace_uuid, u6_block)

# 2. Read satellite board
with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    sat_pcb = f.read()

# Find old J1
j1_ref_pos = sat_pcb.find('Reference" "J1"')
if j1_ref_pos != -1:
    j1_start = sat_pcb.rfind('\t(footprint ', 0, j1_ref_pos)
    j1_end = find_end(sat_pcb, j1_start)
    
    # Replace J1 with new U6 block
    sat_pcb = sat_pcb[:j1_start] + u6_block + sat_pcb[j1_end+1:]
    
    with open('build/icio500/panel_satellite.kicad_pcb', 'w', encoding='utf-8') as f:
        f.write(sat_pcb)
    print('Replaced J1 on satellite board with 20-pin header! Balance =', balance(sat_pcb))
else:
    print('Could not find J1 on satellite board!')
