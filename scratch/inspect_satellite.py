import re

with open('build/icio500/faceplate_front.kicad_pcb', 'r', encoding='utf-8') as f:

    c = f.read()

print("--- Footprints on faceplate_front.kicad_pcb ---")
for m in re.finditer(r'\(footprint\s+"([^"]+)".*?\(at\s+([\d\.-]+)\s+([\d\.-]+)(?:\s+([\d\.-]+))?\)', c, re.DOTALL):
    print(f"Footprint: {m.group(1)} at ({m.group(2)}, {m.group(3)})")

