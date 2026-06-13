import sexpdata
import os

netlist_path = os.path.join('build', 'default.net')
with open(netlist_path, 'r') as f:
    parsed = sexpdata.loads(f.read())

components = []
# parsed[3] is usually (components (comp ...) (comp ...))
for item in parsed:
    if isinstance(item, list) and item and item[0] == sexpdata.Symbol('components'):
        for comp in item[1:]:
            ref = ""
            val = ""
            sheet = ""
            for prop in comp[1:]:
                if prop[0] == sexpdata.Symbol('ref'):
                    ref = prop[1]
                elif prop[0] == sexpdata.Symbol('value'):
                    val = prop[1]
                elif prop[0] == sexpdata.Symbol('sheetpath'):
                    # sheetpath has (names "...")
                    for sprop in prop[1:]:
                        if sprop[0] == sexpdata.Symbol('names'):
                            sheet = sprop[1]
            components.append({'ref': ref, 'val': val, 'sheet': sheet})

groups = {}
for c in components:
    grp = c['sheet'].split('::')[-1] if '::' in c['sheet'] else 'Root'
    if grp not in groups:
        groups[grp] = []
    groups[grp].append(c)

header = """(kicad_sch
	(version 20250114)
	(generator "generate_schematic.py")
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

symbols_text = ""

def add_symbol(ref, val, x, y):
    lib_id = "Device:R" if ref.startswith('R') else "Device:C" if ref.startswith('C') else "Device:D" if ref.startswith('D') else "Device:U"
    sym = f'''
  (symbol (lib_id "{lib_id}") (in_bom yes) (on_board yes)
    (property "Reference" "{ref}" (at {x} {y+3.81} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{val}" (at {x} {y-3.81} 0)
      (effects (font (size 1.27 1.27)))
    )
  )
'''
    return sym

def add_text(text, x, y):
    return f'''
  (text "{text}" (at {x} {y} 0)
    (effects (font (size 2.54 2.54)))
  )
'''

x_offset = 20
y_offset = 20
for grp_name, comps in groups.items():
    symbols_text += add_text(grp_name, x_offset, y_offset - 10)
    for i, c in enumerate(comps):
        px = x_offset + (i % 5) * 20
        py = y_offset + (i // 5) * 20
        symbols_text += add_symbol(c['ref'], c['val'], px, py)
    
    x_offset += 120
    if x_offset > 300:
        x_offset = 20
        y_offset += 100

with open(os.path.join('build', 'icio500', 'generated_schematic.kicad_sch'), 'w') as f:
    f.write(header + symbols_text + footer)

print("Generated schematic at build/icio500/generated_schematic.kicad_sch")
