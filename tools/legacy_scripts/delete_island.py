"""
Delete the isolated copper island (filled_polygon Block 0) from the F.Cu GND zone.
Block 0 is at abs positions 377590..380031 (2442 chars, 88 pts).
It is the small disconnected island near U6 pad 7 at (98.5-101.0, 104.5-107.0).

After deletion, the cached fill will no longer contain the island.
KiCad will regenerate a correct fill when the board is opened.
"""
import re, sys

PCB = 'build/icio500/icio500.kicad_pcb'
content = open(PCB, encoding='utf-8').read()

def balance(s):
    return s.count('(') - s.count(')')

print(f'BEFORE balance: {balance(content)}')
assert balance(content) == 0

# The island block starts at abs pos 377590 (the \t\t(filled_polygon\n)
# Let's verify by finding it precisely
ZONE_UUID = '6a2a9025-1cf9-46ab-a63d-ae791aae11c9'
uuid_pos = content.find(ZONE_UUID)
zone_start = content.rfind('\t(zone\n', 0, uuid_pos)

# Find the first filled_polygon in this zone
fp_start = content.find('\t\t(filled_polygon\n', zone_start)
assert fp_start > zone_start, 'No filled_polygon found in zone'

# Confirm it's near U6 (check coords around 100, 107)
sample = content[fp_start:fp_start+300]
# Extract first few xy coords
coords = re.findall(r'\(xy ([\d.-]+) ([\d.-]+)\)', sample)
print(f'First filled_polygon first coords: {coords[:3]}')

# Verify this is the island (bbox near 98.5-101.0, 104.5-107.0)
if coords:
    x0, y0 = float(coords[0][0]), float(coords[0][1])
    if not (96 < x0 < 104 and 103 < y0 < 110):
        print(f'WARNING: first coord ({x0},{y0}) not near U6 - double-checking...')
        # Find by searching for the small block near U6
        # The island starts with a coord around (99.x, 104.x)
        search = content.find('(xy 99.75663 104.470253)', zone_start)
        if search < 0:
            print('ERROR: island start coord not found')
            sys.exit(1)
        fp_start = content.rfind('\t\t(filled_polygon\n', zone_start, search)
        print(f'Found island at fp_start={fp_start}')

# Find end of this filled_polygon block
depth = 0
fp_end = fp_start
for i in range(fp_start, min(fp_start + 500000, len(content))):
    if content[i] == '(':
        depth += 1
    elif content[i] == ')':
        depth -= 1
        if depth == 0:
            fp_end = i
            break

fp_block = content[fp_start:fp_end+1]
coords_all = re.findall(r'\(xy ([\d.-]+) ([\d.-]+)\)', fp_block)
xs = [float(x) for x,y in coords_all]
ys = [float(y) for x,y in coords_all]
print(f'Island block: {len(fp_block)} chars, {len(coords_all)} pts')
print(f'  bbox: ({min(xs):.2f},{min(ys):.2f})-({max(xs):.2f},{max(ys):.2f})')

# Verify this is definitely the small island, not the main polygon
assert len(coords_all) < 200, f'Too many points ({len(coords_all)}) - this might be the main fill!'
assert max(xs) - min(xs) < 5, 'Too wide - might be main fill!'

print('Confirmed: this is the isolated island. Deleting...')

# Remove the block (include preceding newline if any)
remove_start = fp_start
if remove_start > 0 and content[remove_start-1] == '\n':
    remove_start -= 1

content = content[:remove_start] + content[fp_end+1:]

print(f'AFTER balance: {balance(content)}')
assert balance(content) == 0, 'Unbalanced after deletion!'

open(PCB, 'w', encoding='utf-8').write(content)
print(f'Written. Lines: {content.count(chr(10))}')
