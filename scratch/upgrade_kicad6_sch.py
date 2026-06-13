import re
import os

filepath = r"c:\Users\Chris Williams\Documents\GitHub\ICIO500\build\icio500\schematic.svg\ICIO 3.kicad_sch"
outpath = r"c:\Users\Chris Williams\Documents\GitHub\ICIO500\build\icio500\icio500.kicad_sch"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace U2 value from THAT1246 to THAT1200
content = re.sub(
    r'\(property "Value" "THAT1246"(.*?)\)',
    r'(property "Value" "THAT1200"\1)',
    content
)

# Replace J2 reference to J1
# Wait, J2 is the edge connector. We need to be careful to only replace the Reference property for J2.
content = re.sub(
    r'\(property "Reference" "J2"(.*?)\)',
    r'(property "Reference" "J1"\1)',
    content
)

# Replace OPA2134PA to OPA2134 if needed
content = re.sub(
    r'\(property "Value" "OPA2134PA"(.*?)\)',
    r'(property "Value" "OPA2134"\1)',
    content
)

with open(outpath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Created icio500.kicad_sch from ICIO 3.kicad_sch with mapped values!")
