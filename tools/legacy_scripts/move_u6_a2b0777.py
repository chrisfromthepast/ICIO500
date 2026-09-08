import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Move U6 to 56.0
pcb = re.sub(r'\(at 52\.17 120\.475 180\)', r'(at 56.0 120.475 180)', pcb)

with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)
print("Moved U6 to 56.0")
