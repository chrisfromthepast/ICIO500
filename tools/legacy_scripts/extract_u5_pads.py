import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

nets = [
    'daisy_5v_power', 'audio_in_r', 'i2c1_sda', 'i2c1_scl', 'd13', 'd14',
    'gpio_enc_b', 'gpio_enc_sw', 'spi1_mosi', 'spi1_miso', 'spi1_sck',
    'spi1_cs', 'gpio_disp_dc', 'gpio_disp_res'
]

# Find U5
idx = pcb.find('Reference" "U5"')
start = pcb.rfind('(footprint', 0, idx)
end = pcb.find(')\n  )', idx) + 4
u5_text = pcb[start:end]

# Extract U5 base position
m_at = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?\)', u5_text)
u5_x = float(m_at.group(1))
u5_y = float(m_at.group(2))
u5_rot = float(m_at.group(3)) if m_at.group(3) else 0.0

import math
def rotate(px, py, angle):
    rad = math.radians(angle)
    qx = px * math.cos(rad) - py * math.sin(rad)
    qy = px * math.sin(rad) + py * math.cos(rad)
    return qx, qy

for net_name in nets:
    # Find pad in U5 with this net
    pad_match = re.search(fr'\(pad\s+"(\d+)"[^)]+\(at\s+([\d.-]+)\s+([\d.-]+)\).*?\(net\s+"{net_name}"\)', u5_text, re.DOTALL)
    if not pad_match:
        pad_match = re.search(fr'\(pad\s+"(\d+)".*?\(at\s+([\d.-]+)\s+([\d.-]+)\).*?\(net\s+"{net_name}"\)', u5_text, re.DOTALL)
    
    if pad_match:
        pad_num = pad_match.group(1)
        px = float(pad_match.group(2))
        py = float(pad_match.group(3))
        
        # In KiCad 10, footprint pad coordinates are relative to the footprint!
        rx, ry = rotate(px, py, u5_rot)
        final_x = u5_x + rx
        final_y = u5_y + ry
        print(f"'{net_name}': ({final_x:.3f}, {final_y:.3f}),")
    else:
        print(f"'{net_name}': NOT FOUND IN U5")
