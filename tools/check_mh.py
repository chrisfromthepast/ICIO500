import re
for board in ['faceplate_front', 'panel_satellite', 'icio500']:
 pcbs = open(f'build/icio500/{board}.kicad_pcb').read()
 print(f'\n--- {board} ---')
 for fp in re.finditer(r'\(footprint \".*?MountingHole.*?\".*?\(at ([-.\d]+) ([-.\d]+).*?\)', pcbs, re.DOTALL): print(fp.group(1), fp.group(2))

