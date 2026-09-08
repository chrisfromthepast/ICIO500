import sys

def replace_in_file(filename, old_str, new_str):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    if old_str in content:
        content = content.replace(old_str, new_str)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Replaced in {filename}")
    else:
        print(f"String not found in {filename}: {old_str}")

# Faceplate front
replace_in_file('build/icio500/faceplate_front.kicad_pcb', '(at 19.05 9.5)', '(at 19.05 6.35)')
replace_in_file('build/icio500/faceplate_front.kicad_pcb', '(at 19.05 123.85)', '(at 19.05 127.0)')

# Panel satellite
replace_in_file('build/icio500/panel_satellite.kicad_pcb', '(at 119.05 109.5)', '(at 119.05 106.35)')
replace_in_file('build/icio500/panel_satellite.kicad_pcb', '(at 119.05 223.85)', '(at 119.05 227.0)')
