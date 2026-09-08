import re
import sys

# 1. Read the SMD footprint
with open(r'C:\Program Files\KiCad\10.0\share\kicad\footprints\Connector_PinHeader_2.54mm.pretty\PinHeader_2x10_P2.54mm_Vertical_SMD.kicad_mod', 'r', encoding='utf-8') as f:
    smd_fp = f.read()

# 2. Modify the SMD footprint to have Reference J? (doesn't matter, pcbnew will update it?)
# No, better keep it J1 or J2 (the satellite one is J1 or J2?)
# Let's check panel_satellite.kicad_pcb to see its reference
with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Extract the existing footprint block for PinHeader_2x10_P2.54mm_Vertical
match = re.search(r'\(footprint "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical".*?^\s*\)', pcb, re.DOTALL | re.MULTILINE)
if not match:
    # Try finding it without the library prefix if it was updated
    match = re.search(r'\(footprint "PinHeader_2x10_P2.54mm_Vertical".*?^\s*\)', pcb, re.DOTALL | re.MULTILINE)

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

# Now modify the smd_fp to match these!
# Replace 'PinHeader_2x10_P2.54mm_Vertical_SMD' with 'Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical_SMD'
smd_fp = smd_fp.replace('(footprint "PinHeader_2x10_P2.54mm_Vertical_SMD"', f'(footprint "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical_SMD"\n  (uuid "{uuid}")\n  (at {at})')

# Remove existing version and generator
smd_fp = re.sub(r'\(version [0-9]+\)\n', '', smd_fp)
smd_fp = re.sub(r'\(generator "[^"]+"\)\n', '', smd_fp)

smd_fp = smd_fp.replace('(property "Reference" "REF**"', f'(property "Reference" "{ref}"')
smd_fp = smd_fp.replace('(property "Value" "PinHeader_2x10_P2.54mm_Vertical_SMD"', '(property "Value" "Conn_02x10_Odd_Even"')

# Replace the block
new_pcb = pcb.replace(old_fp_block, smd_fp)

with open('build/icio500/panel_satellite.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(new_pcb)
print("Replaced with SMD footprint.")
