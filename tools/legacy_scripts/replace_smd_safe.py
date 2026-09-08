import re
import sys

# 1. Read the SMD footprint
with open(r'C:\Program Files\KiCad\10.0\share\kicad\footprints\Connector_PinHeader_2.54mm.pretty\PinHeader_2x10_P2.54mm_Vertical_SMD.kicad_mod', 'r', encoding='utf-8') as f:
    smd_fp = f.read()

# 2. Modify the SMD footprint to have Reference J2 (it was J2, or J1)
with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

match = re.search(r'\(footprint "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical".*?\n\t\)', pcb, re.DOTALL)
if not match:
    print("Could not find the connector footprint in panel_satellite.kicad_pcb!")
    sys.exit(1)

old_fp_block = match.group(0)

# Get the uuid
uuid_match = re.search(r'\(uuid "([^"]+)"\)', old_fp_block)
uuid = uuid_match.group(1) if uuid_match else ""

# Get the reference
ref_match = re.search(r'\(property "Reference" "([^"]+)"', old_fp_block)
ref = ref_match.group(1) if ref_match else "J1"

# Get the at
at_match = re.search(r'\(at (.*?)\)', old_fp_block)
at = at_match.group(1) if at_match else "0 0"

# Replace footprint name, uuid, at
smd_fp = smd_fp.replace('(footprint "PinHeader_2x10_P2.54mm_Vertical_SMD"', f'(footprint "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical_SMD"\n  (uuid "{uuid}")\n  (at {at})')
smd_fp = re.sub(r'\(version [0-9]+\)\n', '', smd_fp)
smd_fp = re.sub(r'\(generator "[^"]+"\)\n', '', smd_fp)

# Replace reference and value properties
smd_fp = smd_fp.replace('(property "Reference" "REF**"', f'(property "Reference" "{ref}"')
smd_fp = smd_fp.replace('(property "Value" "PinHeader_2x10_P2.54mm_Vertical_SMD"', '(property "Value" "Conn_02x10_Odd_Even"')

# Replace the block (indentation is 1 tab)
smd_fp = '\t' + smd_fp.replace('\n', '\n\t')
# The last brace will have an extra tab, remove it
if smd_fp.endswith('\n\t'):
    smd_fp = smd_fp[:-2] + '\n'

new_pcb = pcb.replace(old_fp_block, smd_fp)

with open('build/icio500/panel_satellite.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(new_pcb)
print("Replaced with SMD footprint safely.")
