"""
Fix isolated_copper on GND F.Cu zone by setting island_removal_mode to 1.
Zone UUID: 6a2a9025-1cf9-46ab-a63d-ae791aae11c9

island_removal_mode values:
  0 = keep all islands (current - causes DRC warning)
  1 = remove islands smaller than min_island_area
  2 = always remove all islands

We set mode 1 with a reasonable min_island_area (10 mm^2).
This tells KiCad to auto-remove the isolated patch during zone fill.
"""
import re, sys

PCB = 'build/icio500/icio500.kicad_pcb'
ZONE_UUID = '6a2a9025-1cf9-46ab-a63d-ae791aae11c9'

content = open(PCB, encoding='utf-8').read()

def balance(s):
    return s.count('(') - s.count(')')

print(f'BEFORE balance: {balance(content)}')
assert balance(content) == 0

# Find the zone by UUID
uuid_pos = content.find(ZONE_UUID)
assert uuid_pos >= 0, 'Zone UUID not found'

# Find zone block start
zone_start = content.rfind('\t(zone\n', 0, uuid_pos)
assert zone_start >= 0, 'Zone block start not found'

# Find zone block end
depth = 0
zone_end = zone_start
for i in range(zone_start, min(zone_start + 500000, len(content))):
    if content[i] == '(':
        depth += 1
    elif content[i] == ')':
        depth -= 1
        if depth == 0:
            zone_end = i
            break

zone_block = content[zone_start:zone_end+1]
print(f'Zone block: {len(zone_block)} chars')

# Verify it's our zone
assert ZONE_UUID in zone_block, 'UUID not in zone block'
assert 'gnd' in zone_block, 'Not a GND zone'
assert 'F.Cu' in zone_block, 'Not on F.Cu'

# Current island_removal_mode
irm_match = re.search(r'\(island_removal_mode (\d+)\)', zone_block)
if irm_match:
    current_mode = irm_match.group(1)
    print(f'Current island_removal_mode: {current_mode}')
    
    if current_mode == '1' or current_mode == '2':
        print('Already set to remove islands - no change needed')
        sys.exit(0)
    
    # Replace mode 0 with mode 1, and add min_island_area if not present
    old_str = f'(island_removal_mode {current_mode})'
    
    # Check if min_island_area is already set
    if 'min_island_area' in zone_block:
        new_str = '(island_removal_mode 1)'
    else:
        new_str = '(island_removal_mode 1)\n\t\t(min_island_area 10)'
    
    new_zone_block = zone_block.replace(old_str, new_str, 1)
    content = content[:zone_start] + new_zone_block + content[zone_end+1:]
    print(f'Updated island_removal_mode: 0 -> 1')
    if 'min_island_area 10' in new_str:
        print('Added min_island_area: 10 mm^2')
else:
    print('island_removal_mode not found in zone block - adding it')
    # Find a good insertion point - after (fill ...) settings or before (polygon
    # Look for the fill settings block
    fill_match = re.search(r'\(fill\b', zone_block)
    if fill_match:
        # Find end of fill block
        fill_abs = zone_start + fill_match.start()
        depth = 0
        fill_end = fill_abs
        for i in range(fill_abs, min(fill_abs + 2000, len(content))):
            if content[i] == '(':
                depth += 1
            elif content[i] == ')':
                depth -= 1
                if depth == 0:
                    fill_end = i
                    break
        # Insert after fill block
        insert_pos = fill_end + 1
        insert_text = '\n\t\t(island_removal_mode 1)\n\t\t(min_island_area 10)'
        content = content[:insert_pos] + insert_text + content[insert_pos:]
        print('Inserted island_removal_mode 1 after fill block')
    else:
        print('ERROR: cannot find insertion point')
        sys.exit(1)

print(f'AFTER balance: {balance(content)}')
assert balance(content) == 0, 'Unbalanced after edit!'

open(PCB, 'w', encoding='utf-8').write(content)
print(f'Written. Lines: {content.count(chr(10))}')
