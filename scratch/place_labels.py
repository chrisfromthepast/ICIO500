import sys
import re

def parse_erc(report_file):
    with open(report_file, 'r', encoding='utf-8') as f:
        content = f.read()
    coords = set()
    
    # Format:
    # [unconnected_wire_endpoint]: Unconnected wire endpoint
    #     ; warning
    #     @(26.67 mm, 46.99 mm): Horizontal Wire, length 2.54 mm
    #     @(128.27 mm, 78.74 mm): Junction
    
    blocks = content.split('[unconnected_wire_endpoint]:')
    for b in blocks[1:]:
        lines = b.strip().split('\n')
        for line in lines:
            m = re.search(r'@\(([\d\.]+) mm, ([\d\.]+) mm\):.*?Wire', line)
            if m:
                x, y = float(m.group(1)), float(m.group(2))
                coords.add((x, y))
                # Only take the first wire coordinate per error
                break

    return list(coords)

def place_dummy_labels(schem_path, out_path, coords):
    import uuid
    with open(schem_path, 'r', encoding='utf-8') as f:
        content = f.read()

    labels = []
    for i, (x, y) in enumerate(coords):
        net_name = f"NET_FIX_{i}"
        lbl = f"  (global_label \"{net_name}\" (shape input) (at {x:.2f} {y:.2f} 0) (fields_autoplaced) (effects (font (size 1.27 1.27)) (justify left)) (uuid \"{uuid.uuid4()}\") (property \"Intersheetrefs\" \"${{INTERSHEET_REFS}}\" (at 0 0 0) (effects (font (size 1.27 1.27)) hide)))"
        labels.append(lbl)

    print(f"Injecting {len(labels)} placeholder labels...")
    idx = content.rfind('(sheet_instances')
    if idx == -1:
        idx = len(content) - 2
    
    new_content = content[:idx] + '\n'.join(labels) + '\n' + content[idx:]
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == '__main__':
    coords = parse_erc('build/icio500/erc_report.txt')
    place_dummy_labels('build/icio500/generated_schematic.kicad_sch', 'build/icio500/generated_schematic.kicad_sch', coords)
