with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

idx = pcb.find('Reference" "U5"')
if idx != -1:
    start = pcb.rfind('(footprint', 0, idx)
    end = pcb.find(')\n  )', idx)
    if start != -1 and end != -1:
        u5_text = pcb[start:end]
        print(u5_text)
    else:
        print("bounds not found")
else:
    print("U5 not found")
