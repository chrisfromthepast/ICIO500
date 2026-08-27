with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if '(net "d14")' in line:
        print(''.join(lines[max(0, i-4):i+3]))
        print('---')
