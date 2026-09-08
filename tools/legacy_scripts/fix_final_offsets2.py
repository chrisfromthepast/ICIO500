with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

import re

# Update Satellite offsets back to rotated space
pcb = re.sub(
    r'\(model "\./panel_satellite\.step"[\s\S]*?\(offset\s+\(xyz[\s\S]*?\)\s+\)[\s\S]*?\(scale',
    r'(model "./panel_satellite.step"\n      (offset\n        (xyz 0.8 166.675 -119.05)\n      )\n      (scale',
    pcb
)

# Update Faceplate offsets back to rotated space
pcb = re.sub(
    r'\(model "\./faceplate_front\.step"[\s\S]*?\(offset\s+\(xyz[\s\S]*?\)\s+\)[\s\S]*?\(scale',
    r'(model "./faceplate_front.step"\n      (offset\n        (xyz -0.8 66.675 -19.05)\n      )\n      (scale',
    pcb
)

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)

print("Restored original ROTATED offsets (GUI applies Offset AFTER Rotation)")
