import re

with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

def find_pad(ref, pad_num):
    fp_starts = [m.start() for m in re.finditer(r'\n\t\(footprint ', pcb)]
    for idx in range(len(fp_starts)):
        start = fp_starts[idx]
        end = fp_starts[idx + 1] if idx + 1 < len(fp_starts) else len(pcb)
        fp_text = pcb[start:end]
        if f'(property "Reference" "{ref}"' in fp_text:
            at_match = re.search(r'\n\t\t\(at ([\d.e-]+) ([\d.e-]+)(?: ([\d.e-]+))?\)', fp_text)
            if not at_match: continue
            fp_x, fp_y = float(at_match.group(1)), float(at_match.group(2))
            rot = float(at_match.group(3)) if at_match.group(3) else 0.0
            
            # find pad
            pad_match = re.search(r'\(pad "' + str(pad_num) + r'" [^\)]+\(at ([\d.e-]+) ([\d.e-]+)(?: ([\d.e-]+))?\)', fp_text)
            if pad_match:
                px, py = float(pad_match.group(1)), float(pad_match.group(2))
                # simple assuming no rotation for this debug
                print(f"{ref} Pad {pad_num} is at ({fp_x + px}, {fp_y + py})")

find_pad('D8', 1)
find_pad('D8', 2)
find_pad('R8', 1)
find_pad('R8', 2)
