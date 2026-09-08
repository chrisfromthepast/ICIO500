import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

pcb = pcb.replace('(at 52.17 120.475 180)', '(at 52.17 103.825 180)')

with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'r', encoding='utf-8') as f:
    asm = f.read()

asm = asm.replace('(at 52.17 120.475 180)', '(at 52.17 103.825 180)')
# Wait, assembly file might have old U6 position since we copied it when it was 120.475!
asm = asm.replace('(at 93.37 107 90)', '(at 52.17 103.825 180)') # just in case

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(asm)

print("Updated U6 position to match inverted Y")
