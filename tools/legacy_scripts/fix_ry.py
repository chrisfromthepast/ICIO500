import re

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Replace Satellite
pcb = re.sub(r'\(model "\./panel_satellite\.step"[\s\S]*?\(offset[\s\S]*?\(xyz[^\)]+\)', 
             '(model "./panel_satellite.step"\n      (offset\n        (xyz -119.05 166.675 -1.6)', pcb)
pcb = re.sub(r'\(model "\./panel_satellite\.step"[\s\S]*?\(xyz 0 [\d\.-]+ 0\)', 
             lambda m: m.group(0).replace('0 90 0', '0 -90 0'), pcb)

# Replace Faceplate
pcb = re.sub(r'\(model "\./faceplate_front\.step"[\s\S]*?\(offset[\s\S]*?\(xyz[^\)]+\)', 
             '(model "./faceplate_front.step"\n      (offset\n        (xyz -19.05 66.675 -3.2)', pcb)
pcb = re.sub(r'\(model "\./faceplate_front\.step"[\s\S]*?\(xyz 0 [\d\.-]+ 0\)', 
             lambda m: m.group(0).replace('0 90 0', '0 -90 0'), pcb)

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)
print("Updated 3D assembly.")
