import re
import sys

def parse_board(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    components = []
    # Match footprints
    for fp_match in re.finditer(r'\(footprint "([^"]+)"', content):
        start = fp_match.start()
        # Find the end of this footprint block
        depth = 0
        end = start
        for i in range(start, len(content)):
            if content[i] == '(': depth += 1
            elif content[i] == ')':
                depth -= 1
                if depth == 0:
                    end = i
                    break
        fp_block = content[start:end+1]
        
        lib_ref = fp_match.group(1)
        
        # Get Reference
        ref_match = re.search(r'\(property "Reference" "([^"]+)"', fp_block)
        ref = ref_match.group(1) if ref_match else "UNKNOWN"
        
        # Get Position
        at_match = re.search(r'\(at ([\d.-]+) ([\d.-]+)(?: ([\d.-]+))?\)', fp_block)
        if not at_match:
            continue
        x = float(at_match.group(1))
        y = float(at_match.group(2))
        rot = float(at_match.group(3)) if at_match.group(3) else 0.0
        
        components.append({
            'ref': ref,
            'lib_ref': lib_ref,
            'x': x,
            'y': y,
            'rot': rot
        })
    return components

main_board = parse_board('build/icio500/icio500.kicad_pcb')
faceplate = parse_board('build/icio500/faceplate_front.kicad_pcb')
satellite = parse_board('build/icio500/panel_satellite.kicad_pcb')

def print_components(title, comps):
    print(f"=== {title} ===")
    for c in sorted(comps, key=lambda x: x['ref']):
        print(f"  {c['ref']:>5} ({c['lib_ref']:<30}): ({c['x']:>6.2f}, {c['y']:>6.2f}) rot: {c['rot']}")

print_components('Main Board (Pots, Jacks, Switches, Holes)', [c for c in main_board if any(c['ref'].startswith(x) for x in ['RV', 'J', 'SW', 'H', 'U'])])
print_components('Faceplate Front', faceplate)
print_components('Panel Satellite', satellite)
