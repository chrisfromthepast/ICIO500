"""
Add a GND stitching via in the center of the isolated copper island on F.Cu.
Island bbox: (98.46, 104.47) - (100.98, 106.99)
Center: ~(99.72, 105.73)

Via spec: 0.8mm diameter, 0.4mm drill (same as existing GND vias).
"""
import re, sys, uuid

PCB = 'build/icio500/icio500.kicad_pcb'
content = open(PCB, encoding='utf-8').read()

def balance(s):
    return s.count('(') - s.count(')')

print(f'BEFORE balance: {balance(content)}')
assert balance(content) == 0

# Check if there are already vias or pads near (99.72, 105.73)
# U6 is a 2x10 pin header at (93.37, 107, 90deg)
# Pads at 2.54mm pitch. With 90 deg rotation:
#   pad at relative (col*2.54, row*2.54) -> absolute (93.37 - row*2.54, 107 + col*2.54) ... approximately

# Via position: center of the island, slightly offset from pad 5 (98.45, 107.0)
# Choose (99.72, 105.5) - in the island, clear of the pad row at y=107
VIA_X = 99.72
VIA_Y = 105.5
VIA_SIZE = 0.8
VIA_DRILL = 0.4
VIA_UUID = str(uuid.uuid4())

print(f'Adding GND via at ({VIA_X}, {VIA_Y})')

via_block = f"""	(via
		(at {VIA_X} {VIA_Y})
		(size {VIA_SIZE})
		(drill {VIA_DRILL})
		(layers "F.Cu" "B.Cu")
		(net "gnd")
		(uuid "{VIA_UUID}")
	)"""

# Insert before the first zone (or just before closing paren of kicad_pcb)
# Find a good insertion point - just before "(zone" sections start
# Insert after all segments/vias, before first zone
first_zone = content.find('\t(zone\n')
if first_zone < 0:
    print('ERROR: no zone found')
    sys.exit(1)

insert_pos = first_zone
content = content[:insert_pos] + via_block + '\n' + content[insert_pos:]

print(f'AFTER balance: {balance(content)}')
assert balance(content) == 0

open(PCB, 'w', encoding='utf-8').write(content)
print(f'Written. UUID: {VIA_UUID}')
print(f'Lines: {content.count(chr(10))}')
