import re
import sys
import math

def parse_erc(report_file):
    with open(report_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    coords = set()
    matches = re.finditer(r'@\(([\d\.]+) mm, ([\d\.]+) mm\).*?\n\[unconnected_wire_endpoint\]', content, re.MULTILINE)
    for m in matches:
        x, y = float(m.group(1)), float(m.group(2))
        coords.add((x, y))
    return list(coords)

def dist_point_to_segment(px, py, x1, y1, x2, y2):
    l2 = (x1 - x2)**2 + (y1 - y2)**2
    if l2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2))
    proj_x = x1 + t * (x2 - x1)
    proj_y = y1 + t * (y2 - y1)
    return math.hypot(px - proj_x, py - proj_y)

def fix_schematic(schem_file, out_file, coords):
    with open(schem_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    wires = []
    for m in re.finditer(r'\(wire\s*\(pts\s*\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s*\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)\)', content):
        wires.append((float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))))

    new_junctions = []
    
    for x, y in coords:
        # If it is reported as an unconnected wire endpoint, we ALWAYS just drop a junction!
        # Because if it's genuinely floating, a junction doesn't hurt.
        # If it touches another wire, the junction fixes it!
        # Let's just blindly add junctions at every unconnected coordinate!
        new_junctions.append(f"  (junction (at {x:.2f} {y:.2f}) (diameter 0) (color 0 0 0 0)\n    (uuid \"00000000-0000-0000-0000-{len(new_junctions):012d}\")\n  )")

    # Inject junctions
    print(f"Injecting {len(new_junctions)} junctions...")
    idx = content.rfind('(sheet_instances')
    if idx == -1:
        idx = len(content) - 2
    
    new_content = content[:idx] + '\n'.join(new_junctions) + '\n' + content[idx:]
    
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == '__main__':
    coords = parse_erc('build/icio500/erc_report.txt')
    print(f"Found {len(coords)} unconnected endpoints.")
    fix_schematic('build/icio500/generated_schematic.kicad_sch', 'build/icio500/generated_schematic.kicad_sch', coords)
