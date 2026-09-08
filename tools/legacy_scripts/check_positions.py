import re

def check_board(filename):
    print(f"\n--- {filename} ---")
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Match (footprint "Lib:Name" \n (layer "...") \n (uuid "...") \n (at X Y [Rot])
    # Or just match (footprint "Name" and the very next (at X Y)
    footprints = re.findall(r'\(footprint\s+"([^"]+)"[\s\S]*?\(at\s+([0-9.-]+)\s+([0-9.-]+)(?:\s+([0-9.-]+))?\)', content)
    for name, x, y, rot in footprints:
        if "MountingHole" in name or "PinHeader" in name:
            print(f"Footprint {name} at ({x}, {y}) rot={rot}")

check_board('build/icio500/panel_satellite.kicad_pcb')
check_board('build/icio500/icio500.kicad_pcb')
check_board('build/icio500/faceplate_front.kicad_pcb')
