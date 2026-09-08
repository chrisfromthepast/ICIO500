import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# U6
pcb = re.sub(
    r'\(footprint "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical"([\s\S]*?\(at )[\d\.-]+ [\d\.-]+ [\d\.-]*(\)',
    r'(footprint "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Horizontal"\g<1>52.17 120.475 180)',
    pcb
)
pcb = re.sub(
    r'PinHeader_2x10_P2.54mm_Vertical\.step',
    r'PinHeader_2x10_P2.54mm_Horizontal.step',
    pcb
)
with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)


with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    sat = f.read()

# J1
sat = re.sub(
    r'\(footprint "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical_SMD"([\s\S]*?\(layer "F.Cu"\)[\s\S]*?\(at )[\d\.-]+ [\d\.-]+ [\d\.-]*(\)',
    r'(footprint "Connector_PinSocket_2.54mm:PinSocket_2x10_P2.54mm_Vertical_SMD"\g<1>119.05 175.0 0)',
    sat
)
# Wait, it might be on B.Cu already
sat = re.sub(
    r'\(footprint "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical_SMD"([\s\S]*?\(at )[\d\.-]+ [\d\.-]+ [\d\.-]*(\)',
    r'(footprint "Connector_PinSocket_2.54mm:PinSocket_2x10_P2.54mm_Vertical_SMD"\n\t\t(layer "B.Cu")\n\t\t\g<1>119.05 175.0 0)',
    sat
)

# And replace the 3D model
sat = re.sub(
    r'Connector_PinHeader_2.54mm\.3dshapes/PinHeader_2x10_P2.54mm_Vertical_SMD\.step',
    r'Connector_PinSocket_2.54mm.3dshapes/PinSocket_2x10_P2.54mm_Vertical_SMD.step',
    sat
)
with open('build/icio500/panel_satellite.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(sat)

print("Updated footprints robustly")
