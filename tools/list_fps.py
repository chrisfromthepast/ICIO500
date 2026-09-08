import re
pcbs = open('build/icio500/icio500.kicad_pcb').read()
fps = re.findall(r'\(footprint \"([^"]*)\"', pcbs)
for f in sorted(set(fps)): print(f)
