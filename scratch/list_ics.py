import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

def get_footprints():
    fps = []
    pos = 0
    while True:
        idx = pcb.find('(footprint ', pos)
        if idx == -1: break
        depth = 0
        end = idx
        for i in range(idx, len(pcb)):
            if pcb[i] == '(': depth += 1
            elif pcb[i] == ')':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        block = pcb[idx:end]
        ref_m = re.search(r'\(property "Reference" "([^"]+)"', block)
        at_m = re.search(r'\(at ([-\d.]+) ([-\d.]+) ?([-\d.]*)\)', block)
        if ref_m and at_m:
            ref = ref_m.group(1)
            x = float(at_m.group(1))
            y = float(at_m.group(2))
            rot = float(at_m.group(3)) if at_m.group(3) else 0.0
            fps.append((ref, x, y, rot))
        pos = idx + 10
    return fps

fps = get_footprints()
print(f"Total footprints: {len(fps)}")
# Filter for ICs and key components:
for ref, x, y, rot in sorted(fps, key=lambda f: f[0]):
    if ref.startswith('U') or ref.startswith('J') or ref.startswith('MH'):
        print(f"  {ref:8s}: at ({x:7.2f}, {y:7.2f}), rot {rot:6.1f}")
