import re
import uuid

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Make sure we start from a clean state without the autorouter garbage
# But wait, a2b0777 has U6 at 52.17, 120.475
pcb = re.sub(r'\(at 52\.17 120\.475 180\)', r'(at 56.0 120.475 180)', pcb)

endpoints = {
    'daisy_5v_power': (86.5, 112.0),
    'audio_in_r': (93.37, 104.46),
    'i2c1_sda': (95.91, 104.46),
    'i2c1_scl': (98.45, 104.46),
    'd13': (95.4, 112.5),  # Approximate targets
    'd14': (92.8, 112.5),
    'gpio_enc_b': (90.3, 112.5),
    'gpio_enc_sw': (87.7, 112.5),
    'spi1_mosi': (106.07, 104.46),
    'spi1_miso': (108.61, 107.00),
    'spi1_sck': (109.88, 105.73),
    'spi1_cs': (111.15, 107.00),
    'gpio_disp_dc': (112.42, 105.73),
    'gpio_disp_res': (113.69, 107.00),
}

pads = {
    'daisy_5v_power': (56.0, 120.475),
    'audio_in_r': (53.46, 120.475),
    'i2c1_sda': (53.46, 117.935),
    'i2c1_scl': (53.46, 115.395),
    'd13': (53.46, 112.855),
    'd14': (56.0, 110.315),
    'gpio_enc_b': (53.46, 110.315),
    'gpio_enc_sw': (56.0, 107.775),
    'spi1_mosi': (53.46, 107.775),
    'spi1_miso': (56.0, 105.235),
    'spi1_sck': (53.46, 105.235),
    'spi1_cs': (56.0, 102.695),
    'gpio_disp_dc': (53.46, 102.695),
    'gpio_disp_res': (56.0, 100.155),
}

new_segments = []

def add_segment(sx, sy, ex, ey, layer, net_name):
    uid = str(uuid.uuid4())
    seg = f'\n  (segment\n    (start {sx:.4f} {sy:.4f})\n    (end {ex:.4f} {ey:.4f})\n    (width 0.25)\n    (layer "{layer}")\n    (net "{net_name}")\n    (uuid "{uid}")\n  )'
    new_segments.append(seg)

def add_via(x, y, net_name):
    uid = str(uuid.uuid4())
    # Via layers are F.Cu to B.Cu by default in KiCad, which covers all inner layers too
    via = f'\n  (via\n    (at {x:.4f} {y:.4f})\n    (size 0.8)\n    (drill 0.4)\n    (layers "F.Cu" "B.Cu")\n    (net "{net_name}")\n    (uuid "{uid}")\n  )'
    new_segments.append(via)

channel_x = 60.0
for i, (net, (px, py)) in enumerate(pads.items()):
    if net not in endpoints: continue
    tx, ty = endpoints[net]
    
    vx1 = channel_x + i * 1.5
    add_segment(px, py, vx1, py, "In1.Cu", net)
    add_via(vx1, py, net)
    
    add_segment(vx1, py, vx1, ty, "In2.Cu", net)
    add_via(vx1, ty, net)
    
    vx2 = tx - 1.0
    add_segment(vx1, ty, vx2, ty, "In1.Cu", net)
    add_via(vx2, ty, net)
    
    for l in ["F.Cu", "B.Cu", "In1.Cu", "In2.Cu"]:
        add_segment(vx2, ty, tx, ty, l, net)

# GND vias
gnd_pads = [(56.0, 117.935), (56.0, 115.395), (56.0, 112.855)]
for px, py in gnd_pads:
    add_via(px + 2.0, py, "gnd")
    add_segment(px, py, px + 2.0, py, "F.Cu", "gnd")
    add_segment(px, py, px + 2.0, py, "B.Cu", "gnd")

insert_pos = pcb.rfind('\n)')
pcb = pcb[:insert_pos] + ''.join(new_segments) + pcb[insert_pos:]

with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)
print(f"Added {len(new_segments)} routing items.")
