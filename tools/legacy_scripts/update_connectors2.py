import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Replace U6 footprint name, position, rotation, and 3D model
pcb = re.sub(
    r'\(footprint "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical"[\s\S]*?\(uuid "95a8ff09-0c0b-4a44-8b4a-0e353805373d"\)\s+\(at [\d\.-]+ [\d\.-]+ [\d\.-]*\)',
    r'(footprint "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Horizontal"\n\t\t(layer "F.Cu")\n\t\t(uuid "95a8ff09-0c0b-4a44-8b4a-0e353805373d")\n\t\t(at 52.17 120.475 180)',
    pcb
)
pcb = re.sub(
    r'\(model "\$\{KICAD10_3DMODEL_DIR\}/Connector_PinHeader_2.54mm\.3dshapes/PinHeader_2x10_P2.54mm_Vertical\.step"[\s\S]*?\(rotate[\s\S]*?\)\n\t\t\)',
    r'(model "/Connector_PinHeader_2.54mm.3dshapes/PinHeader_2x10_P2.54mm_Horizontal.step"\n\t\t\t(offset\n\t\t\t\t(xyz 0 0 0)\n\t\t\t)\n\t\t\t(scale\n\t\t\t\t(xyz 1 1 1)\n\t\t\t)\n\t\t\t(rotate\n\t\t\t\t(xyz 0 0 0)\n\t\t\t)\n\t\t)',
    pcb
)

with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)


with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    sat = f.read()

sat = re.sub(
    r'\(footprint "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical_SMD"[\s\S]*?\(at [\d\.-]+ [\d\.-]+ [\d\.-]*\)',
    r'(footprint "Connector_PinSocket_2.54mm:PinSocket_2x10_P2.54mm_Vertical_SMD"\n\t\t(layer "B.Cu")\n\t\t(uuid "ab56372f-4472-468c-806e-d61d438ca140")\n\t\t(at 119.05 175.0 0)',
    sat
)
sat = re.sub(
    r'\(model "\$\{KICAD10_3DMODEL_DIR\}/Connector_PinHeader_2.54mm\.3dshapes/PinHeader_2x10_P2.54mm_Vertical_SMD\.step"[\s\S]*?\(rotate[\s\S]*?\)\n\t\t\)',
    r'(model "/Connector_PinSocket_2.54mm.3dshapes/PinSocket_2x10_P2.54mm_Vertical_SMD.step"\n\t\t\t(offset\n\t\t\t\t(xyz 0 0 0)\n\t\t\t)\n\t\t\t(scale\n\t\t\t\t(xyz 1 1 1)\n\t\t\t)\n\t\t\t(rotate\n\t\t\t\t(xyz 0 0 0)\n\t\t\t)\n\t\t)',
    sat
)
# wait, J1 might have a different UUID! Let's just use string replacement carefully!
