import re

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

models = re.findall(r'\(model\s+"([^"]+)"', pcb)
print('3D Models found in assembly:')
for m in set(models):
    print(f'  {m}')

# Let's specifically look at the footprint Cards:EDA_306
eda_start = pcb.find('Cards:EDA_306')
if eda_start > 0:
    eda_block = pcb[eda_start:eda_start+1000]
    print('\nEDA_306 block models:')
    print(re.findall(r'\(model\s+"([^"]+)"', eda_block))
