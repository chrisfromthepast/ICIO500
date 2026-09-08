import re

endpoints = {
    'daisy_5v_power': (86.5, 112.0),
    'audio_in_r': (93.37, 104.46),
    'i2c1_sda': (95.91, 104.46),
    'i2c1_scl': (98.45, 104.46),
    'd13': (95.4, 112.5),
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

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

segs = re.findall(r'\(segment\n\s*\(start\s+([\d.-]+)\s+([\d.-]+)\)\n\s*\(end\s+([\d.-]+)\s+([\d.-]+)\).*?\(layer\s+"([^"]+)".*?\(net\s+"([^"]+)"\)', pcb, re.DOTALL)

print("Found", len(segs), "segments")
for net, (ex, ey) in endpoints.items():
    found = False
    for sx, sy, dx, dy, layer, seg_net in segs:
        if seg_net == net:
            sx, sy, dx, dy = float(sx), float(sy), float(dx), float(dy)
            # Check if this segment connects to our endpoint
            if abs(sx - ex) < 0.5 and abs(sy - ey) < 0.5:
                print(f"{net} endpoint is on {layer}")
                found = True
                break
            if abs(dx - ex) < 0.5 and abs(dy - ey) < 0.5:
                print(f"{net} endpoint is on {layer}")
                found = True
                break
    if not found:
        print(f"Could not find endpoint for {net}")
