content = open('build/icio500/icio500.kicad_pcb', encoding='utf-8').read()
opens = content.count('(')
closes = content.count(')')
print(f'Opens: {opens}, Closes: {closes}, Delta: {opens-closes}')
in_str = False
for i, c in enumerate(content):
    if c == '"': in_str = not in_str
print(f'Ends in string: {in_str}')
print(f'File size: {len(content)} bytes, lines: {content.count(chr(10))}')
# Check last 200 chars
print('Last 200 chars:')
print(repr(content[-200:]))
