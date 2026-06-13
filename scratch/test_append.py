import os
import shutil

# Copy the original
shutil.copy('build/icio500/icio500.kicad_sch', 'scratch/test_append.kicad_sch')

with open('scratch/test_append.kicad_sch', 'r') as f:
    content = f.read()

# Remove the trailing )
content = content.strip()
if content.endswith(')'):
    content = content[:-1]

# Append a resistor symbol
resistor_symbol = """
  (symbol (lib_id "Device:R") (in_bom yes) (on_board yes)
    (property "Reference" "R10" (at 5.08 0 90)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "10k" (at 0 0 90)
      (effects (font (size 1.27 1.27)))
    )
  )
"""

content += resistor_symbol + "\n)\n"

with open('scratch/test_append.kicad_sch', 'w') as f:
    f.write(content)

print("Appended resistor symbol to test_append.kicad_sch")
