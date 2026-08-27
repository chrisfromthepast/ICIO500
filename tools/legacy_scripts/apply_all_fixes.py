"""
Replay all good fixes on the restored HEAD:
1. Delete d14 dangling via (UUID: df0a3bee-e540-4fb2-9dce-f9d533c73126)
2. Add zone_connect 2 to C19 pad 2 (UUID: 73f0b786-e895-4f54-88b2-cbbde73e5da1)
3. Add zone_connect 2 to ALL GND pads of U6 (the 2x10 pin header)
4. Set island_removal_mode 1 on F.Cu GND zone (UUID: 6a2a9025)

Verifies balance at every step.
"""
import re, sys

PCB = 'build/icio500/icio500.kicad_pcb'
content = open(PCB, encoding='utf-8').read()

D14_VIA_UUID    = 'df0a3bee-e540-4fb2-9dce-f9d533c73126'
C19_PAD2_UUID   = '73f0b786-e895-4f54-88b2-cbbde73e5da1'
U6_REF          = '"U6"'
GND_ZONE_UUID   = '6a2a9025-1cf9-46ab-a63d-ae791aae11c9'

def balance(s):
    return s.count('(') - s.count(')')

def find_block_end(content, start, max_chars=500000):
    depth = 0
    for i in range(start, min(start + max_chars, len(content))):
        if content[i] == '(': depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    return -1

print(f'BEFORE balance: {balance(content)}')
assert balance(content) == 0

# ---- FIX 1: Delete d14 via ----
uuid_pos = content.find(D14_VIA_UUID)
assert uuid_pos >= 0
via_start = content.rfind('\t(via\n', 0, uuid_pos)
via_end = find_block_end(content, via_start)
via_block = content[via_start:via_end+1]
assert 'd14' in via_block and D14_VIA_UUID in via_block
remove_start = via_start - 1 if content[via_start-1] == '\n' else via_start
content = content[:remove_start] + content[via_end+1:]
assert balance(content) == 0
print('Fix 1: d14 via deleted OK')

# ---- FIX 2: zone_connect 2 on C19 pad 2 ----
uuid_pos = content.find(C19_PAD2_UUID)
assert uuid_pos >= 0
pad_start = content.rfind('\t\t(pad "2"', 0, uuid_pos)
pad_end = find_block_end(content, pad_start)
pad_block = content[pad_start:pad_end+1]
assert 'net "gnd"' in pad_block and 'zone_connect' not in pad_block
content = content[:pad_end] + '\n\t\t\t(zone_connect 2)' + content[pad_end:]
assert balance(content) == 0
print('Fix 2: C19 pad 2 zone_connect 2 OK')

# ---- FIX 3: zone_connect 2 on ALL GND pads of U6 ----
u6_pos = content.find(U6_REF)
assert u6_pos >= 0
fp_start = content.rfind('\t(footprint', 0, u6_pos)
fp_end = find_block_end(content, fp_start)
fp_block = content[fp_start:fp_end+1]
print(f'U6 footprint: {len(fp_block)} chars')

# Find all GND pads in U6
gnd_pad_count = 0
# We'll collect patches to apply (in reverse order to preserve positions)
patches = []  # list of (pad_end_abs, insert_text)

for m in re.finditer(r'\t\t\(pad "[^"]+" thru_hole', fp_block):
    pad_start_in_fp = m.start()
    pad_abs = fp_start + pad_start_in_fp
    pad_end_abs = find_block_end(content, pad_abs, 2000)
    pad_blk = content[pad_abs:pad_end_abs+1]
    
    if 'net "gnd"' in pad_blk and 'zone_connect' not in pad_blk:
        pad_num_m = re.search(r'\(pad "(\w+)"', pad_blk)
        pad_num = pad_num_m.group(1) if pad_num_m else '?'
        patches.append((pad_end_abs, '\n\t\t\t(zone_connect 2)', pad_num))
        gnd_pad_count += 1

print(f'U6 GND pads without zone_connect: {gnd_pad_count}')

# Apply patches in reverse order (highest position first)
for pad_end_abs, insert_text, pad_num in sorted(patches, key=lambda x: -x[0]):
    content = content[:pad_end_abs] + insert_text + content[pad_end_abs:]
    assert balance(content) == 0
    
print(f'Fix 3: zone_connect 2 added to {gnd_pad_count} U6 GND pads OK')

# ---- FIX 4: island_removal_mode 1 on F.Cu GND zone ----
uuid_pos = content.find(GND_ZONE_UUID)
zone_start = content.rfind('\t(zone\n', 0, uuid_pos)
zone_end = find_block_end(content, zone_start, 500000)
zone_block = content[zone_start:zone_end+1]

irm_match = re.search(r'\(island_removal_mode (\d+)\)', zone_block)
assert irm_match, 'island_removal_mode not found'
current_mode = irm_match.group(1)
print(f'Fix 4: island_removal_mode {current_mode} -> 1')

if current_mode != '1':
    old = f'(island_removal_mode {current_mode})'
    new = '(island_removal_mode 1)'
    new_zone = zone_block.replace(old, new, 1)
    content = content[:zone_start] + new_zone + content[zone_end+1:]
    assert balance(content) == 0
    print('Fix 4: island_removal_mode set to 1 OK')
else:
    print('Fix 4: already set to 1, no change')

# ---- Write ----
print(f'\nFINAL balance: {balance(content)}')
assert balance(content) == 0
open(PCB, 'w', encoding='utf-8').write(content)
print(f'Written. Lines: {content.count(chr(10))}, Size: {len(content)} bytes')
