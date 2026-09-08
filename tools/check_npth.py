import re
pcbs = open('build/icio500/icio500.kicad_pcb').read()
print('\n'.join(re.findall(r'\(pad .*?np_thru_hole.*?\)', pcbs, re.DOTALL)))
