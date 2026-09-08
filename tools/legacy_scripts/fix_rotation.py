import re

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Replace Satellite
pcb = re.sub(r'\(model "\./panel_satellite\.step"[\s\S]*?\(offset[\s\S]*?\(xyz[^\)]+\)[\s\S]*?\(scale[\s\S]*?\(xyz[^\)]+\)[\s\S]*?\(rotate[\s\S]*?\(xyz[^\)]+\)', 
             '(model "./panel_satellite.step"\n      (offset\n        (xyz 0.8 166.675 -119.05)\n      )\n      (scale\n        (xyz 1 1 1)\n      )\n      (rotate\n        (xyz 0 90 0)', pcb)

# Replace Faceplate
pcb = re.sub(r'\(model "\./faceplate_front\.step"[\s\S]*?\(offset[\s\S]*?\(xyz[^\)]+\)[\s\S]*?\(scale[\s\S]*?\(xyz[^\)]+\)[\s\S]*?\(rotate[\s\S]*?\(xyz[^\)]+\)', 
             '(model "./faceplate_front.step"\n      (offset\n        (xyz -0.8 66.675 -19.05)\n      )\n      (scale\n        (xyz 1 1 1)\n      )\n      (rotate\n        (xyz 0 90 0)', pcb)

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)
print("Applied positive 90 rotation and matching offsets.")
