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

# Move connector to the right edge, aligned with main board connector
replace_in_file('build/icio500/panel_satellite.kicad_pcb', '(at 119.05 103.50 90)', '(at 133.0 161.5 90)')
