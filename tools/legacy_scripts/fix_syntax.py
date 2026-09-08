with open('build/icio500/faceplate_front.kicad_pcb', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    # If it's the very last occurrence (near end of file), keep it
    if "(embedded_fonts no)" in line:
        if i < len(lines) - 5: # If it's not at the very end
            continue
    new_lines.append(line)

with open('build/icio500/faceplate_front.kicad_pcb', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
