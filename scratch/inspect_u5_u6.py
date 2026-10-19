import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Let's parse all footprints by finding (footprint ... and matching parens
def get_footprints():
    fps = {}
    pos = 0
    while True:
        idx = pcb.find('(footprint ', pos)
        if idx == -1: break
        # find matching paren
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
        m = re.search(r'\(property "Reference" "([^"]+)"', block)
        if m:
            ref = m.group(1)
            fps[ref] = block
        pos = idx + 10
    return fps

fps = get_footprints()
print(f"Total footprints: {len(fps)}")

for ref in ['U5', 'U6']:
    if ref in fps:
        print(f"*** {ref} ***")
        lines = fps[ref].splitlines()
        for l in lines[:10]:
            print(l)
    else:
        print(f"{ref} not found, checking similar keys...")
        for k in fps:
            if 'U' in k or 'Seed' in k or 'Daisy' in k:
                print(' ', k)
