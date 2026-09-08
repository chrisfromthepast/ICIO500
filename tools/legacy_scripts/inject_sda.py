import re

with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

segment = '''
  (segment (start 103.0 150.5) (end 107.5 175.5) (width 0.25) (layer "F.Cu") (net "i2c1_sda"))
'''
# We need to find the actual net ID for i2c1_sda
net_match = re.search(r'\(net (\d+) "i2c1_sda"\)', pcb)
if net_match:
    net_id = net_match.group(1)
    segment = segment.replace('"i2c1_sda"', f'{net_id} "i2c1_sda"')
    
    insert_pos = pcb.rfind('\n)')
    pcb = pcb[:insert_pos] + segment + pcb[insert_pos:]
    
    with open('build/icio500/panel_satellite.kicad_pcb', 'w', encoding='utf-8') as f:
        f.write(pcb)
    print("Injected SDA segment.")
