import re
pcbs = open('build/icio500/icio500.kicad_pcb').read()
m = re.search(r'\(footprint \"Cards:EDA_306\"(.*?)\n  \)', pcbs, re.DOTALL)
if m: print(m.group(0)[:1000])
