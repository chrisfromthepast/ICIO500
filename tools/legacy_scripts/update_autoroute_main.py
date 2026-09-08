with open('tools/legacy_scripts/autoroute_main.py', 'r', encoding='utf-8') as f:
    text = f.read()
text = text.replace("PCB_PATH = 'build/icio500/panel_satellite.kicad_pcb'", "PCB_PATH = 'build/icio500/icio500.kicad_pcb'")
with open('tools/legacy_scripts/autoroute_main.py', 'w', encoding='utf-8') as f:
    f.write(text)
