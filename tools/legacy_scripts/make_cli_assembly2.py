import re

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Replace Satellite
pcb = re.sub(r'\(model "\./panel_satellite\.step"[\s\S]*?\(offset[\s\S]*?\(xyz[^\)]+\)', 
             '(model "./panel_satellite.step"\n      (offset\n        (xyz -119.05 166.675 -0.8)', pcb)

# Replace Faceplate
pcb = re.sub(r'\(model "\./faceplate_front\.step"[\s\S]*?\(offset[\s\S]*?\(xyz[^\)]+\)', 
             '(model "./faceplate_front.step"\n      (offset\n        (xyz -19.05 66.675 -2.4)', pcb)

with open('build/icio500/cli_render_assembly2.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)
print("Created CLI-specific assembly file.")
