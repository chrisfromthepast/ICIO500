import re

def get_bbox(pcb_path):
    with open(pcb_path, 'r', encoding='utf-8') as f:
        text = f.read()
    pts = []
    for m in re.finditer(r'\(gr_line\s+\(start\s+([\d.-]+)\s+([\d.-]+)\)\s+\(end\s+([\d.-]+)\s+([\d.-]+)\)\s+.*\(layer\s+"?Edge\.Cuts"?\)', text):
        pts.extend([(float(m.group(1)), float(m.group(2))), (float(m.group(3)), float(m.group(4)))])
    for m in re.finditer(r'\(gr_arc\s+.*\(start\s+([\d.-]+)\s+([\d.-]+)\)\s+\(mid\s+([\d.-]+)\s+([\d.-]+)\)\s+\(end\s+([\d.-]+)\s+([\d.-]+)\)\s+.*\(layer\s+"?Edge\.Cuts"?\)', text):
        pts.extend([(float(m.group(1)), float(m.group(2))), (float(m.group(5)), float(m.group(6)))])
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return {
        'min_x': min(xs), 'min_y': min(ys),
        'max_x': max(xs), 'max_y': max(ys),
        'width': max(xs) - min(xs),
        'height': max(ys) - min(ys)
    }

print('Main board (icio500.kicad_pcb):', get_bbox('build/icio500/icio500.kicad_pcb'))
print('Faceplate front (faceplate_front.kicad_pcb):', get_bbox('build/icio500/faceplate_front.kicad_pcb'))
print('Panel satellite (panel_satellite.kicad_pcb):', get_bbox('build/icio500/panel_satellite.kicad_pcb'))
