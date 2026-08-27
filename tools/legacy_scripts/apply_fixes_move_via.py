import re
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add zone_connect 2 to C19 pad 2
C19_PAD2_UUID = '73f0b786-e895-4f54-88b2-cbbde73e5da1'
uuid_pos = content.find(C19_PAD2_UUID)
pad_start = content.rfind('\t\t(pad "2"', 0, uuid_pos)
pad_end = content.find(')', content.find(')', content.find(')', pad_start)+1)+1)+20 # rough but we can just use the balance func
def balance(s): return s.count('(') - s.count(')')
def find_end(content, start):
    depth = 0
    for i in range(start, len(content)):
        if content[i] == '(': depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0: return i
    return -1
pad_end = find_end(content, pad_start)
content = content[:pad_end] + '\n\t\t\t(zone_connect 2)' + content[pad_end:]

# 2. Add zone_connect 2 to U6 GND pads
u6_pos = content.find('"U6"')
fp_start = content.rfind('\t(footprint', 0, u6_pos)
fp_end = find_end(content, fp_start)
fp_block = content[fp_start:fp_end+1]
patches = []
for m in re.finditer(r'\t\t\(pad "[^"]+" thru_hole', fp_block):
    pad_abs = fp_start + m.start()
    pad_end_abs = find_end(content, pad_abs)
    pad_blk = content[pad_abs:pad_end_abs+1]
    if 'net "gnd"' in pad_blk and 'zone_connect' not in pad_blk:
        patches.append((pad_end_abs, '\n\t\t\t(zone_connect 2)'))
for pad_end_abs, insert_text in sorted(patches, key=lambda x: -x[0]):
    content = content[:pad_end_abs] + insert_text + content[pad_end_abs:]

# 3. Move the dangling d14 via to stitch the GND island!
D14_VIA_UUID = 'df0a3bee-e540-4fb2-9dce-f9d533c73126'
uuid_pos = content.find(D14_VIA_UUID)
via_start = content.rfind('\t(via', 0, uuid_pos)
via_end = find_end(content, via_start)

# Replace the via block
new_via = f"""	(via
		(at 99.0 105.0)
		(size 0.8)
		(drill 0.4)
		(layers "F.Cu" "B.Cu")
		(net "gnd")
		(uuid "{D14_VIA_UUID}")
	)"""
content = content[:via_start] + new_via + content[via_end+1:]

with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(content)
print('Applied 3 fixes and moved via to (99.0, 105.0) on GND')
