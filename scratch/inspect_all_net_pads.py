import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    c = f.read()

# find all footprints and their references
fps = {}
for m in re.finditer(r'\(footprint\s+"([^"]+)"[\s\S]*?\(property\s+"Reference"\s+"([^"]+)"', c):
    ref = m.group(2)
    start = m.start()
    # find end of footprint
    depth = 0
    end = start
    for i in range(start, len(c)):
        if c[i] == '(': depth += 1
        elif c[i] == ')':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    fps[ref] = c[start:end]

print("Pins for U5 nets across the whole board:")
target_nets = [
    'daisy_5v_power', 'audio_in_r', 'daisy_audio_in', 'audio_out_r', 'audio_in_from_daisy_plus'
]
for net in ['daisy_audio_in', 'audio_in_from_daisy_plus']:
    print(f"\nPads for {net}:")
    for ref, block in fps.items():
        for pm in re.finditer(r'\(pad\s+"([^"]+)"[^\n]*\n\s*\(at\s+([-\d.]+)\s+([-\d.]+)[^\)]*\)[\s\S]*?\(net\s+"' + net + r'"\)', block):
            at_m = re.search(r'\(at ([-\d.]+) ([-\d.]+) ?([-\d.]*)\)', block)
            print(f"  {ref} pin {pm.group(1)} at fp ({at_m.group(1)}, {at_m.group(2)})")


