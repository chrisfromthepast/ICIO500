"""
Clean two-change fix to HEAD PCB:
1. Delete the d14 dangling via (UUID: look up from file)
2. Add zone_connect 2 (solid fill) to C19 pad 2

Run AFTER verifying HEAD DRC baseline.
"""
import re, sys

PCB = 'build/icio500/icio500.kicad_pcb'
content = open(PCB, encoding='utf-8').read()

# Verify balance before
opens = content.count('(')
closes = content.count(')')
print(f'BEFORE - Opens: {opens}, Closes: {closes}, Delta: {opens-closes}')
if opens != closes:
    print('ERROR: HEAD file is already unbalanced. Stopping.')
    sys.exit(1)

# ---- FIX 1: Delete d14 via ----
# Find the via with net d14. The via was at approximately (155.575, 77.055)
# Look for all vias with net "d14"
via_pattern = re.compile(
    r'\t\(via\b.*?\(net "d14"\).*?\)',
    re.DOTALL
)
matches = list(via_pattern.finditer(content))
print(f'Found {len(matches)} via(s) with net d14')
for m in matches:
    print(f'  pos {m.start()}: {repr(m.group(0)[:100])}')

if len(matches) == 1:
    # Find full via block (nested parens)
    start = matches[0].start()
    depth = 0
    end = start
    for i in range(start, min(start + 500, len(content))):
        if content[i] == '(': depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                end = i
                break
    via_block = content[start:end+1]
    print(f'Deleting via block ({end-start+1} chars):')
    print(repr(via_block[:200]))
    
    # Delete it (include leading newline/tab)
    delete_start = start
    if delete_start > 0 and content[delete_start-1] == '\n':
        delete_start -= 1
    content = content[:delete_start] + content[end+1:]
    print('Via d14 deleted.')
else:
    print('Skipping via deletion - unexpected match count')

# ---- FIX 2: Add zone_connect 2 to C19 pad 2 ----
# Find pad 2 of C19 by looking for it near the C19 reference
c19_ref_pos = content.find('"C19"')
if c19_ref_pos < 0:
    print('ERROR: C19 not found')
    sys.exit(1)

# Find footprint start
fp_start = content.rfind('\t(footprint', 0, c19_ref_pos)
print(f'C19 footprint starts at pos {fp_start}')

# Find end of footprint
depth = 0
fp_end = fp_start
for i in range(fp_start, min(fp_start + 200000, len(content))):
    if content[i] == '(': depth += 1
    elif content[i] == ')':
        depth -= 1
        if depth == 0:
            fp_end = i
            break

fp_block = content[fp_start:fp_end+1]
print(f'C19 footprint: {len(fp_block)} chars')

# Find pad "2" with net "gnd" in the footprint
pad2_match = re.search(r'\t\t\(pad "2" smd', fp_block)
if not pad2_match:
    print('ERROR: pad 2 not found in C19 footprint')
    sys.exit(1)

pad2_abs_start = fp_start + pad2_match.start()
depth = 0
pad2_end = pad2_abs_start
for i in range(pad2_abs_start, min(pad2_abs_start + 1000, len(content))):
    if content[i] == '(':
        depth += 1
    elif content[i] == ')':
        depth -= 1
        if depth == 0:
            pad2_end = i
            break

pad_block = content[pad2_abs_start:pad2_end+1]
print(f'C19 pad 2 block ({pad2_end-pad2_abs_start+1} chars):')
print(repr(pad_block[:200]))

if 'zone_connect' in pad_block:
    print('zone_connect already set - skipping')
elif 'net "gnd"' not in pad_block:
    print('ERROR: pad 2 is not gnd net! Stopping.')
    sys.exit(1)
else:
    # Insert (zone_connect 2) before closing )
    content = content[:pad2_end] + '\n\t\t\t(zone_connect 2)' + content[pad2_end:]
    print('Added (zone_connect 2) to C19 pad 2')

# Verify balance after
opens = content.count('(')
closes = content.count(')')
print(f'\nAFTER - Opens: {opens}, Closes: {closes}, Delta: {opens-closes}')
if opens != closes:
    print('ERROR: File became unbalanced! Not writing.')
    sys.exit(1)

open(PCB, 'w', encoding='utf-8').write(content)
print(f'Written OK. Lines: {content.count(chr(10))}')
