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

pads = []
for pm in re.finditer(r'\(pad\s+"(\d+)"[^\n]*\n\s*\(at\s+([-\d.]+)\s+([-\d.]+)[^\)]*\)[\s\S]*?\(net\s+"([^"]*)"\)', block):
    num = int(pm.group(1))
    lx = float(pm.group(2))
    ly = float(pm.group(3))
    net = pm.group(4)
    pads.append((num, lx, ly, net))

pads.sort(key=lambda x: x[0])
for pm in re.finditer(r'\(pad\s+"([^"]+)"[^\n]*\n\s*\(at\s+([-\d.]+)\s+([-\d.]+)[^\)]*\)[\s\S]*?\(net\s+"gpio_disp_res"\)', block):
    print(pm.group(0))


