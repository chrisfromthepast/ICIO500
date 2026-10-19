import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('"Reference" "U5"')
start = c.rfind('(footprint', 0, idx)
depth = 0
end = start
for i in range(start, len(c)):
    if c[i] == '(': depth += 1
    elif c[i] == ')':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
block = c[start:end]

for pm in re.finditer(r'\(pad\s+"(\d+)"[^\n]*\n\s*\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?', block):
    num = int(pm.group(1))
    if num in [1, 2, 20, 21, 40]:
        print(f"Pad {num:2d}: at {pm.group(2)} {pm.group(3)} rot={pm.group(4)}")
