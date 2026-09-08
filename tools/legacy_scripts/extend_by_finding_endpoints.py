import re
import uuid

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

pcb = re.sub(r'\(at 52\.17 103\.825 180\)', r'(at 56.0 103.825 180)', pcb)

# (net "gpio_disp_res") -> net is a string with quotes!
# Wait, some might be numbers if they are vias, but segments have string nets usually in this context.
# Let's match anything inside the net parens.
segments = re.findall(r'\(\s*segment\s*\(\s*start\s+([\d\.]+)\s+([\d\.]+)\s*\)\s*\(\s*end\s+([\d\.]+)\s+([\d\.]+)\s*\)\s*\(\s*width\s+([\d\.]+)\s*\)\s*\(\s*layer\s+"(.*?)"\s*\)\s*\(\s*net\s+(.*?)\s*\)', pcb)

new_segments = []
for sx, sy, ex, ey, width, layer, net in segments:
    sx, sy, ex, ey = float(sx), float(sy), float(ex), float(ey)
    
    for px, py in [(sx, sy), (ex, ey)]:
        if (abs(px - 52.2) < 0.5 or abs(px - 49.6) < 0.5) and 80 < py < 120:
            uid = str(uuid.uuid4())
            nx = px + 3.83
            new_seg = f'\n  (segment\n    (start {px:.4f} {py:.4f})\n    (end {nx:.4f} {py:.4f})\n    (width {width})\n    (layer "{layer}")\n    (net {net})\n    (uuid "{uid}")\n  )'
            new_segments.append(((px, py), new_seg))
            break

unique_segments = {k: v for k, v in new_segments}

insert_pos = pcb.rfind('\n)')
pcb = pcb[:insert_pos] + ''.join(unique_segments.values()) + pcb[insert_pos:]

with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)
print(f"Moved U6 and added {len(unique_segments)} extension tracks.")
