import re
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

u5_block = re.search(r'\(footprint "Package_DIP:DIP-40_W15\.24mm_Socket".*?\n  \)', pcb, re.DOTALL)
if u5_block:
    pads = re.findall(r'\(pad\s+"(\d+)".*?\(at\s+([\d.-]+)\s+([\d.-]+)\).*?\(net\s+\d+\s+"([^"]+)"\)', u5_block.group(0))
    for p in pads:
        print(f'U5 Pin {p[0]}: {p[3]} at Y={p[2]}')
else:
    print("Could not find DIP-40")
