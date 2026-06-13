import re
import math

def parse_kicad5_sch(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    components = []
    wires = []
    texts = []
    
    in_comp = False
    curr_comp = {}
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('$Comp'):
            in_comp = True
            curr_comp = {'fields': {}}
        elif line.startswith('$EndComp'):
            in_comp = False
            components.append(curr_comp)
        elif in_comp:
            parts = line.split()
            if not parts:
                i += 1
                continue
            if parts[0] == 'L':
                curr_comp['lib'] = parts[1]
                curr_comp['ref'] = parts[2]
            elif parts[0] == 'P':
                curr_comp['x'] = int(parts[1])
                curr_comp['y'] = int(parts[2])
            elif parts[0] == 'F':
                # F 0 "U2" H 3950 3900 50  0000 L CNN
                field_id = int(parts[1])
                # Extract quoted string
                m = re.search(r'"(.*?)"', line)
                if m:
                    curr_comp['fields'][field_id] = m.group(1)
            elif len(parts) == 4 and all(p.lstrip('-').isdigit() for p in parts):
                # Matrix: 1 0 0 -1
                curr_comp['matrix'] = f"{parts[0]} {parts[1]} {parts[2]} {parts[3]}"
        elif line.startswith('Wire Wire Line'):
            i += 1
            pts = lines[i].strip().split()
            wires.append((int(pts[0]), int(pts[1]), int(pts[2]), int(pts[3])))
        elif line.startswith('Text GLabel'):
            # Text GLabel 800  3850 0    50   Output ~ 0
            # Next line is the text
            parts = line.split()
            x, y = int(parts[2]), int(parts[3])
            i += 1
            text = lines[i].strip()
            texts.append({'type': 'GLabel', 'x': x, 'y': y, 'text': text})
        
        i += 1
        
    return components, wires, texts

def matrix_to_rot(m):
    mapping = {
        "1 0 0 -1": (0, ""),
        "0 1 1 0": (90, ""),
        "-1 0 0 1": (180, ""),
        "0 -1 -1 0": (270, ""),
        "-1 0 0 -1": (0, "(mirror x)"),
        "1 0 0 1": (0, "(mirror y)"),
        "0 1 -1 0": (90, "(mirror x)"),
        "0 -1 1 0": (90, "(mirror y)"),
        "1 0 0 1": (0, "(mirror y)"),
        "0 1 -1 0": (270, "(mirror y)")
    }
    return mapping.get(m, (0, ""))

def generate_kicad6(components, wires, texts, outpath):
    header = """(kicad_sch
	(version 20250114)
	(generator "translate_sch.py")
	(generator_version "1.0")
	(uuid "0cbb3bbb-8297-40d4-b3a9-e92b3d8d375c")
	(paper "A3")
	(title_block
		(title "ICIO500 Translated Schematic")
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
    
    out = [header]
    
    # Scale factor from mils to mm
    S = 0.0254
    
    for w in wires:
        out.append(f'  (wire (pts (xy {w[0]*S:.2f} {w[1]*S:.2f}) (xy {w[2]*S:.2f} {w[3]*S:.2f})) (stroke (width 0) (type default)))\n')
        
    for t in texts:
        out.append(f'  (global_label "{t["text"]}" (shape input) (at {t["x"]*S:.2f} {t["y"]*S:.2f} 0) (effects (font (size 1.27 1.27))))\n')

    for c in components:
        ref = c.get('fields', {}).get(0, c.get('ref', 'U?'))
        val = c.get('fields', {}).get(1, '')
        x = c.get('x', 0) * S
        y = c.get('y', 0) * S
        
        angle, mirror = matrix_to_rot(c.get('matrix', '1 0 0 -1'))
        
        lib_id = "Device:U"
        if ref.startswith('R'): lib_id = "Device:R"
        elif ref.startswith('C'): lib_id = "Device:C"
        elif ref.startswith('D'): lib_id = "Device:D"
        elif ref.startswith('L'): lib_id = "Device:L"
        elif ref.startswith('J'): lib_id = "Connector_Generic:Conn_01x15"
        elif ref.startswith('#PWR'):
            lib_id = "power:" + val
        
        # Override specific ICs
        if '1246' in val:
            lib_id = "Amplifier_Audio:THAT1200"
            val = "THAT1200"
        elif '1646' in val:
            lib_id = "Amplifier_Audio:THAT1646"
            val = "THAT1646"
        elif '2134' in val:
            lib_id = "Amplifier_Operational:OPA2134"
            val = "OPA2134"
            
        sym = f"""  (symbol (lib_id "{lib_id}") (in_bom yes) (on_board yes)
    (property "Reference" "{ref}" (at {x} {y-2.54} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{val}" (at {x} {y+2.54} 0) (effects (font (size 1.27 1.27))))
  )
"""
        # wait, we must apply translation to the symbol block!
        sym = f"""  (symbol (lib_id "{lib_id}") (in_bom yes) (on_board yes) (at {x:.2f} {y:.2f} {angle}) {mirror}
    (property "Reference" "{ref}" (at {x:.2f} {(y-2.54):.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{val}" (at {x:.2f} {(y+2.54):.2f} 0) (effects (font (size 1.27 1.27))))
  )
"""
        out.append(sym)
        
    out.append(footer)
    
    with open(outpath, 'w') as f:
        f.write("".join(out))

if __name__ == '__main__':
    comps, wires, texts = parse_kicad5_sch('ICIO 3.sch')
    generate_kicad6(comps, wires, texts, 'build/icio500/generated_schematic.kicad_sch')
    print("Successfully translated ICIO 3.sch to generated_schematic.kicad_sch!")
