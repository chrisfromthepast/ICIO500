import re
import uuid

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    content = f.read()

def balance(s): return s.count('(') - s.count(')')
def find_end(content, start):
    depth = 0
    for i in range(start, len(content)):
        if content[i] == '(': depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0: return i
    return -1

# 1. Add zone_connect 2 to C19 pad 2
C19_PAD2_UUID = '73f0b786-e895-4f54-88b2-cbbde73e5da1'
uuid_pos = content.find(C19_PAD2_UUID)
pad_start = content.rfind('\t\t(pad "2"', 0, uuid_pos)
pad_end = find_end(content, pad_start)
content = content[:pad_end] + '\n\t\t\t(zone_connect 2)' + content[pad_end:]

# 2. Add zone_connect 2 to U6 GND pads
U6_PAD7_UUID = 'e444e20b-db2b-4839-8f41-e674ee2fa850'
pad_uuid_pos = content.find(U6_PAD7_UUID)
fp_start = content.rfind('\t(footprint ', 0, pad_uuid_pos)
fp_end = find_end(content, fp_start)
fp_block = content[fp_start:fp_end+1]

patches = []
for m in re.finditer(r'\t\t\(pad "([^"]+)" thru_hole', fp_block):
    pad_num = m.group(1)
    pad_abs = fp_start + m.start()
    pad_end_abs = find_end(content, pad_abs)
    pad_blk = content[pad_abs:pad_end_abs+1]
    if 'net "gnd"' in pad_blk and 'zone_connect' not in pad_blk:
        patches.append((pad_end_abs, '\n\t\t\t(zone_connect 2)'))

for pad_end_abs, insert_text in sorted(patches, key=lambda x: -x[0]):
    content = content[:pad_end_abs] + insert_text + content[pad_end_abs:]

# 3. Delete the d14 dangling via completely
D14_VIA_UUID = 'df0a3bee-e540-4fb2-9dce-f9d533c73126'
uuid_pos = content.find(D14_VIA_UUID)
via_start = content.rfind('\t(via\n', 0, uuid_pos)
via_end = find_end(content, via_start)

# Add a track on F.Cu from Pad 5 (98.45 107.0) to Pad 7 (100.99 107.0)
TRACK_UUID = str(uuid.uuid4())
new_track = f"""	(segment
		(start 98.45 107.0)
		(end 100.99 107.0)
		(width 0.25)
		(layer "F.Cu")
		(net "gnd")
		(uuid "{TRACK_UUID}")
	)"""

# Replace the via with the track
content = content[:via_start] + new_track + content[via_end+1:]

with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. Balance={balance(content)}')
