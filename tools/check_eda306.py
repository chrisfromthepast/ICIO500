import re
pcbs = open('build/icio500/icio500.kicad_pcb').read()
m = re.search(r'\(footprint \"Cards:EDA_306\"(.*?)\(footprint', pcbs, re.DOTALL)
if m: print('\n'.join(re.findall(r'\(pad.*?\)', m.group(1))))
