with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

import re
# Find U6 position
start = pcb.find('property "Reference" "U6"')
if start != -1:
    # Find the (footprint before it)
    fp_start = pcb.rfind('(footprint ', 0, start)
    if fp_start != -1:
        # replace the footprint type
        fp_end = pcb.find('\n', fp_start)
        old_line = pcb[fp_start:fp_end]
        new_line = old_line.replace('PinHeader_2x10_P2.54mm_Vertical', 'PinHeader_2x10_P2.54mm_Horizontal')
        pcb = pcb[:fp_start] + new_line + pcb[fp_end:]
        
        # replace the (at X Y R)
        at_start = pcb.find('(at ', fp_start)
        at_end = pcb.find(')', at_start)
        pcb = pcb[:at_start] + '(at 52.17 120.475 180' + pcb[at_end:]

pcb = pcb.replace('PinHeader_2x10_P2.54mm_Vertical.step', 'PinHeader_2x10_P2.54mm_Horizontal.step')

with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)


with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    sat = f.read()

# J1
start = sat.find('property "Reference" "J1"')
if start != -1:
    fp_start = sat.rfind('(footprint ', 0, start)
    if fp_start != -1:
        fp_end = sat.find('\n', fp_start)
        old_line = sat[fp_start:fp_end]
        new_line = old_line.replace('Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical_SMD', 'Connector_PinSocket_2.54mm:PinSocket_2x10_P2.54mm_Vertical_SMD')
        sat = sat[:fp_start] + new_line + sat[fp_end:]
        
        layer_start = sat.find('(layer ', fp_start)
        layer_end = sat.find(')', layer_start)
        sat = sat[:layer_start] + '(layer "B.Cu"' + sat[layer_end:]

        at_start = sat.find('(at ', fp_start)
        at_end = sat.find(')', at_start)
        sat = sat[:at_start] + '(at 119.05 175.0 0' + sat[at_end:]

sat = sat.replace('Connector_PinHeader_2.54mm.3dshapes/PinHeader_2x10_P2.54mm_Vertical_SMD.step', 'Connector_PinSocket_2.54mm.3dshapes/PinSocket_2x10_P2.54mm_Vertical_SMD.step')

with open('build/icio500/panel_satellite.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(sat)

print("Updated via simple string manipulation")
