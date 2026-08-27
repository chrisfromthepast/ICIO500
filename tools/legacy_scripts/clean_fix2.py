"""
Precise two-change fix:
1. Delete Via 25 (d14 net, UUID: df0a3bee-e540-4fb2-9dce-f9d533c73126) - dangling via
2. Add (zone_connect 2) to C19 pad 2 (GND) - fix starved thermal

Verifies paren balance before and after writing.
"""
import re, sys

PCB = 'build/icio500/icio500.kicad_pcb'
content = open(PCB, encoding='utf-8').read()

D14_VIA_UUID = 'df0a3bee-e540-4fb2-9dce-f9d533c73126'
C19_PAD2_UUID = '73f0b786-e895-4f54-88b2-cbbde73e5da1'

def count_balance(s):
    return s.count('(') - s.count(')')

print(f'BEFORE - Balance: {count_balance(content)} (must be 0)')
assert count_balance(content) == 0, 'File not balanced before changes!'

# ---- FIX 1: Delete d14 via by UUID ----
uuid_pos = content.find(D14_VIA_UUID)
if uuid_pos < 0:
    print(f'ERROR: d14 via UUID not found')
    sys.exit(1)

# Walk back to find the enclosing (via
via_start = content.rfind('\t(via\n', 0, uuid_pos)
if via_start < 0:
    print('ERROR: could not find via block start')
    sys.exit(1)

# Walk forward to find closing )
depth = 0
via_end = via_start
for i in range(via_start, min(via_start + 500, len(content))):
    if content[i] == '(':
        depth += 1
    elif content[i] == ')':
        depth -= 1
        if depth == 0:
            via_end = i
            break

via_block = content[via_start:via_end+1]
print(f'Deleting via block ({via_end - via_start + 1} chars):')
print('  net:', re.search(r'\(net "([^"]+)"\)', via_block).group(1))
print('  at:', re.search(r'\(at ([^\)]+)\)', via_block).group(1))
print('  uuid:', re.search(r'\(uuid "([^"]+)"\)', via_block).group(1))

# Verify it's the d14 via
assert 'd14' in via_block, 'ERROR: via block does not contain d14!'
assert D14_VIA_UUID in via_block, 'ERROR: UUID mismatch!'

# Remove: also eat the preceding newline
remove_start = via_start
if remove_start > 0 and content[remove_start - 1] == '\n':
    remove_start -= 1
content = content[:remove_start] + content[via_end + 1:]
print(f'Via d14 deleted. New balance: {count_balance(content)}')
assert count_balance(content) == 0, 'Unbalanced after via deletion!'

# ---- FIX 2: Add (zone_connect 2) to C19 pad 2 ----
pad2_uuid_pos = content.find(C19_PAD2_UUID)
if pad2_uuid_pos < 0:
    print('ERROR: C19 pad 2 UUID not found')
    sys.exit(1)

# Walk back to find pad block start
pad_start = content.rfind('\t\t(pad "2"', 0, pad2_uuid_pos)
if pad_start < 0:
    print('ERROR: pad block start not found')
    sys.exit(1)

# Walk forward to closing )
depth = 0
pad_end = pad_start
for i in range(pad_start, min(pad_start + 1000, len(content))):
    if content[i] == '(':
        depth += 1
    elif content[i] == ')':
        depth -= 1
        if depth == 0:
            pad_end = i
            break

pad_block = content[pad_start:pad_end+1]
print(f'\nC19 pad 2 block ({pad_end - pad_start + 1} chars):')
assert 'net "gnd"' in pad_block, 'ERROR: pad 2 is not GND!'
assert 'zone_connect' not in pad_block, 'zone_connect already set!'

# Insert (zone_connect 2) just before the closing )
content = content[:pad_end] + '\n\t\t\t(zone_connect 2)' + content[pad_end:]
print(f'Added (zone_connect 2). New balance: {count_balance(content)}')
assert count_balance(content) == 0, 'Unbalanced after zone_connect!'

# ---- Write ----
open(PCB, 'w', encoding='utf-8').write(content)
print(f'\nSUCCESS. Written {len(content)} bytes, {content.count(chr(10))} lines.')
