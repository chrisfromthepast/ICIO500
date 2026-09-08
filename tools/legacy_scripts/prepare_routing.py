import os
import subprocess
import re

# 1. Checkout the clean state
subprocess.run(['git', 'checkout', 'a2b0777', 'build/icio500/icio500.kicad_pcb'])

# 2. Move U6 to 56.0
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

pcb = re.sub(r'\(at 52\.17 120\.475 180\)', r'(at 56.0 120.475 180)', pcb)

# 3. Save
with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)

print("Board ready for routing.")
