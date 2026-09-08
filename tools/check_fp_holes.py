import re
pcbs = open('build/icio500/faceplate_front.kicad_pcb').read()
for fp in re.finditer(r'\(footprint.*?\)', pcbs, re.DOTALL):
 print(fp.group(0)[:100])
