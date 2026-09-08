import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

u6_idx = pcb.find('PinHeader_2x10_P2.54mm_Horizontal')
if u6_idx != -1:
    u6_block = pcb[u6_idx:u6_idx+2000]
    print(u6_block)
