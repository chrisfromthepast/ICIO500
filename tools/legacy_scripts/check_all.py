import re
with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    content = f.read()
footprints = re.findall(r'\(footprint\s+"([^"]+)"[\s\S]*?\(at\s+([0-9.-]+)\s+([0-9.-]+)(?:\s+([0-9.-]+))?\)', content)
for name, x, y, rot in footprints:
    print(f"{name} at ({x}, {y}) rot={rot}")
