"""Remove jog segments by line number and fix C19 pad2 zone_connect."""
import re

PCB = 'build/icio500/icio500.kicad_pcb'
lines = open(PCB, encoding='utf-8').readlines()

print(f'Total lines: {len(lines)}')

# Find lines containing our 3 jog segment UUIDs
target_uuids = {
    '6b8609f4-5066-4d8b-a287-e7a770f21c7d',
    'fc469c70-612d-4a54-aa5b-634d068907ec',
    '17127324-5a85-4893-b39c-bba748093571',
}

uuid_lines = {}
for i, line in enumerate(lines):
    for uid in target_uuids:
        if uid in line:
            uuid_lines[uid] = i
            print(f'UUID {uid[:8]} found at line {i+1}')

# For each UUID, find the enclosing segment block
lines_to_remove = set()
for uid, uuid_line_idx in uuid_lines.items():
    # Search backward for (segment
    start = uuid_line_idx
    while start > 0 and '(segment' not in lines[start]:
        start -= 1
    # Search forward for closing )
    end = uuid_line_idx
    depth = 0
    for j in range(start, min(start+20, len(lines))):
        l = lines[j].strip().rstrip('\r')
        depth += l.count('(') - l.count(')')
        end = j
        if depth <= 0:
            break
    print(f'  Block lines {start+1}..{end+1}')
    for k in range(start, end+1):
        lines_to_remove.add(k)

print(f'Removing {len(lines_to_remove)} lines')
new_lines = [l for i, l in enumerate(lines) if i not in lines_to_remove]
print(f'Lines after removal: {len(new_lines)}')

# Now fix C19 pad 2 zone_connect
content = ''.join(new_lines)

# Find C19 footprint, then pad "2" with net gnd, add zone_connect 2 (solid)
# Pattern: pad "2" ... (net "gnd") ... no existing zone_connect
def add_zone_connect(content):
    # Find the C19 footprint
    c19_start = None
    for m in re.finditer(r'\(reference "C19"\)', content):
        # Walk back to find the footprint opening
        idx = m.start()
        # Find opening paren of enclosing footprint
        depth = 0
        for i in range(idx, max(0, idx-10000), -1):
            if content[i] == ')':
                depth += 1
            elif content[i] == '(':
                depth -= 1
                if depth < 0:
                    c19_start = i
                    break
        break
    
    if c19_start is None:
        print('ERROR: C19 footprint start not found')
        return content

    # Find end of footprint
    depth = 0
    c19_end = c19_start
    for i in range(c19_start, len(content)):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                c19_end = i
                break

    fp_block = content[c19_start:c19_end+1]
    print(f'C19 footprint: chars {c19_start}..{c19_end}')

    # Find pad "2" with net "gnd" in the footprint block
    pad_pattern = re.compile(
        r'\(pad "2".*?\(net "gnd"\)',
        re.DOTALL
    )
    pm = pad_pattern.search(fp_block)
    if not pm:
        print('ERROR: pad 2/gnd not found in C19')
        return content

    # Check if zone_connect already present
    pad_text = pm.group(0)
    if 'zone_connect' in pad_text:
        print('zone_connect already set on C19 pad 2')
        return content

    # Find closing paren of this pad block
    pad_abs_start = c19_start + pm.start()
    depth = 0
    pad_end = pad_abs_start
    for i in range(pad_abs_start, min(pad_abs_start + 2000, len(content))):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                pad_end = i
                break

    # Insert (zone_connect 2) before the closing )
    # Find the last ) of the pad block and insert before it
    insert_at = pad_end  # position of closing )
    # Add zone_connect solid (2) — find the right indentation
    pad_snippet = content[pad_abs_start:pad_end+1]
    # Get indentation of last line before )
    last_nl = content.rfind('\n', pad_abs_start, pad_end)
    indent = '\t\t'
    
    new_content = (
        content[:pad_end] +
        f'\n{indent}(zone_connect 2)' +
        content[pad_end:]
    )
    print(f'Added (zone_connect 2) to C19 pad 2 at position {pad_end}')
    return new_content

content = add_zone_connect(content)
open(PCB, 'w', encoding='utf-8').write(content)
print(f'Written. Final lines: {content.count(chr(10))}')
