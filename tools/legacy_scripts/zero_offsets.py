import re

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Set satellite offset to 0,0,0
pcb = re.sub(r'\(model "\./panel_satellite\.step"[\s\S]*?\(offset[\s\S]*?\(xyz[^\)]+\)', 
             '(model "./panel_satellite.step"\n      (offset\n        (xyz 0 0 0)', pcb)

# Set faceplate offset to -1.6,0,0
pcb = re.sub(r'\(model "\./faceplate_front\.step"[\s\S]*?\(offset[\s\S]*?\(xyz[^\)]+\)', 
             '(model "./faceplate_front.step"\n      (offset\n        (xyz -1.6 0 0)', pcb)

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)
print("Offsets fixed to zero!")
