with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_u6 = False
for line in lines:
    if 'footprint "Connector_PinHeader_2.54mm:PinHeader_2x10' in line:
        in_u6 = True
    if in_u6:
        print(line, end='')
        if '(model' in line:
            break
