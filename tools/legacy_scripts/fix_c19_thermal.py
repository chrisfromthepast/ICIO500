"""Remove jog segments and fix C19 pad2 starved thermal via zone_connect=solid."""
import re

PCB = 'build/icio500/icio500.kicad_pcb'
content = open(PCB, encoding='utf-8').read()

# Remove the 3 jog segments by their UUIDs
uuids_to_remove = [
    '6b8609f4-5066-4d8b-a287-e7a770f21c7d',
    'fc469c70-612d-4a54-aa5b-634d068907ec',
    '17127324-5a85-4893-b39c-bba748093571',
]

for uid in uuids_to_remove:
    # Match the whole segment block containing this UUID
    pattern = re.compile(
        r'\s*\(segment\s*\r?\n(?:[^\)]*\r?\n)*?[^\)]*' + re.escape(uid) + r'[^\)]*\r?\n\s*\)\r?\n',
        re.MULTILINE
    )
    m = pattern.search(content)
    if m:
        content = content[:m.start()] + '\n' + content[m.end():]
        print(f'Removed segment {uid[:8]}...')
    else:
        print(f'WARNING: segment {uid[:8]}... not found')

open(PCB, 'w', encoding='utf-8').write(content)
print('Done removing jog segments.')
print(f'File lines: {content.count(chr(10))}')

# Now find C19 pad 2 in the footprint and add zone_connect override
# C19 pad 2 is at absolute (159.5, 78.0), net "gnd"
# Find its pad entry and add (zone_connect 2) for solid fill
content2 = open(PCB, encoding='utf-8').read()

# Find pad 2 of C19 - look for the footprint containing "C19" reference
# Strategy: find footprint block with C19 ref, then find pad "2" within it
fp_match = re.search(
    r'(\(footprint .*?"C19".*?\n\s*\))\s*\n',
    content2, re.DOTALL
)
if fp_match:
    fp_block = fp_match.group(1)
    print(f'\nFound C19 footprint block ({len(fp_block)} chars)')
    # Find pad 2 within it
    pad_match = re.search(
        r'(\(pad "2" \w+ \w+.*?)(\(net "gnd"\))',
        fp_block, re.DOTALL
    )
    if pad_match:
        print('Found pad 2 with gnd net')
    else:
        print('pad 2/gnd not found in footprint block')
        # Show pad lines
        for line in fp_block.split('\n'):
            if 'pad' in line.lower():
                print(' ', line.strip())
else:
    print('C19 footprint not found by simple search')
    # Try alternate
    for m in re.finditer(r'"C19"', content2):
        start = max(0, m.start()-2000)
        snippet = content2[start:m.start()+500]
        print('Context around C19:', snippet[-200:])
        break
