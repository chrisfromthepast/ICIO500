import os

header = """(kicad_sch
	(version 20250114)
	(generator "gen_sch.py")
	(generator_version "1.0")
	(uuid "0cbb3bbb-8297-40d4-b3a9-e92b3d8d375c")
	(paper "A3")
	(title_block
		(title "ICIO500 Block Diagram / Schematic")
		(rev "1")
	)
"""

footer = """
	(sheet_instances
		(path "/"
			(page "1")
		)
	)
)
"""

symbols = []

def add_symbol(lib_id, ref, val, x, y, rot=0):
    sym = f"""
  (symbol (lib_id "{lib_id}") (in_bom yes) (on_board yes)
    (property "Reference" "{ref}" (at {x} {y+3.81} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{val}" (at {x} {y-3.81} 0)
      (effects (font (size 1.27 1.27)))
    )
    (symbol "{lib_id}_1_1"
      (pin passive line (at {x-5.08} {y} 0) (length 2.54) (name "1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
      (pin passive line (at {x+5.08} {y} 180) (length 2.54) (name "2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
    )
  )
"""
    symbols.append(sym)

def add_label(net, x, y, rot=0):
    label = f"""
  (global_label "{net}" (shape input) (at {x} {y} {rot})
    (effects (font (size 1.27 1.27)) (justify left))
  )
"""
    symbols.append(label)

def add_wire(x1, y1, x2, y2):
    wire = f"""
  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))
    (stroke (width 0) (type default))
  )
"""
    symbols.append(wire)

# PSU Block
add_symbol("Device:D", "D1", "C2480", 50, 50)
add_symbol("Device:D", "D2", "C2480", 50, 70)
add_symbol("Device:C", "C1", "100uF", 70, 50)
add_symbol("Device:C", "C3", "100uF", 70, 70)
add_symbol("Converter_DCDC:MGJ2D091505SC", "U1", "MGJ2D091505SC", 100, 60)

# Input Block
add_symbol("Device:R", "R1", "100R", 50, 120)
add_symbol("Device:R", "R2", "100R", 50, 140)
add_symbol("Device:C", "C9", "220pF", 70, 130)
add_symbol("Amplifier_Audio:THAT1200", "U2", "THAT1200", 110, 130)

# Daisy Seed
add_symbol("MCU_Module:Daisy_Seed", "U5", "Daisy Seed", 160, 130)

# Output Block
add_symbol("Amplifier_Audio:THAT1646", "U4", "THAT1646", 220, 130)
add_symbol("Device:R", "R7", "50R", 250, 120)
add_symbol("Device:R", "R8", "50R", 250, 140)

content = header + "".join(symbols) + footer

with open("scratch/generated.kicad_sch", "w") as f:
    f.write(content)

print("Generated schematic!")
