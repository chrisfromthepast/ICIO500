with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

import re

# Update Satellite offsets
pcb = re.sub(
    r'\(model "\./panel_satellite\.step"[\s\S]*?\(offset\s+\(xyz[\s\S]*?\)\s+\)[\s\S]*?\(scale',
    r'(model "./panel_satellite.step"\n      (offset\n        (xyz -119.05 166.675 -0.8)\n      )\n      (scale',
    pcb
)

# Update Faceplate offsets
pcb = re.sub(
    r'\(model "\./faceplate_front\.step"[\s\S]*?\(offset\s+\(xyz[\s\S]*?\)\s+\)[\s\S]*?\(scale',
    r'(model "./faceplate_front.step"\n      (offset\n        (xyz -38.1 58.35 -0.8)\n      )\n      (scale',
    pcb
)

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)

print("Applied perfectly calculated UNROTATED offsets")
