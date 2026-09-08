with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

idx = pcb.find('Reference" "U6"')
start = pcb.rfind('(footprint', 0, idx)
end = pcb.find(')\n  )', idx)
print(pcb[start:start+500])
