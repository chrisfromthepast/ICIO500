"""
Fix two remaining electrical DRC issues:
1. U6 pad 7 starved thermal (B.Cu) -> add zone_connect 2 (solid fill)
2. isolated_copper on GND F.Cu zone -> examine and handle

Also verify paren balance before and after.
"""
import re, sys

PCB = 'build/icio500/icio500.kicad_pcb'
content = open(PCB, encoding='utf-8').read()

U6_PAD7_UUID = 'e444e20b-db2b-4839-8f41-e674ee2fa850'

def balance(s):
    return s.count('(') - s.count(')')

print(f'BEFORE balance: {balance(content)}')
assert balance(content) == 0

# ---- FIX 1: Add zone_connect 2 to U6 pad 7 ----
uuid_pos = content.find(U6_PAD7_UUID)
assert uuid_pos >= 0, 'U6 pad 7 UUID not found'

pad_start = content.rfind('\t\t(pad "7"', 0, uuid_pos)
assert pad_start >= 0, 'pad 7 block start not found'

depth = 0
pad_end = pad_start
for i in range(pad_start, min(pad_start + 1000, len(content))):
    if content[i] == '(': depth += 1
    elif content[i] == ')':
        depth -= 1
        if depth == 0:
            pad_end = i
            break

pad_block = content[pad_start:pad_end+1]
assert 'net "gnd"' in pad_block, 'U6 pad 7 is not GND!'
assert 'zone_connect' not in pad_block, 'zone_connect already set!'

content = content[:pad_end] + '\n\t\t\t(zone_connect 2)' + content[pad_end:]
print(f'Added zone_connect 2 to U6 pad 7. Balance: {balance(content)}')
assert balance(content) == 0

open(PCB, 'w', encoding='utf-8').write(content)
print(f'Written. Lines: {content.count(chr(10))}')
print()
print('NOTE: isolated_copper will be evaluated in the next DRC run.')
print('It is likely caused by the B.Cu zone isolation around U6 pad 7 -')
print('fixing the starved thermal with solid fill may also resolve it.')
