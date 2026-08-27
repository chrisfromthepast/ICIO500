content = open('build/icio500/icio500.kicad_pcb', encoding='utf-8').read()
depth = 0
for i, c in enumerate(content):
    if c == '(': depth += 1
    elif c == ')': depth -= 1
    if depth < 0:
        start = max(0, i-100)
        print(f'Negative depth at pos {i}:')
        print(repr(content[start:i+50]))
        break
print(f'Final depth: {depth}')
# Find the orphan ( by tracking last position where depth goes from 0 to 1
depth = 0
orphan_pos = -1
for i, c in enumerate(content):
    if c == '(':
        if depth == 0:
            orphan_pos = i
        depth += 1
    elif c == ')':
        depth -= 1
print(f'Orphan ( at pos {orphan_pos}')
print(repr(content[orphan_pos:orphan_pos+300]))
