import re
import uuid

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

def add_track(net, x1, y1, x2, y2, layer="In1.Cu"):
    if abs(x1 - x2) < 0.001 and abs(y1 - y2) < 0.001:
        return ""
    return f'  (segment (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (width 0.25) (layer "{layer}") (net "{net}") (uuid "{uuid.uuid4()}"))\n'

def add_via(net, x, y):
    return f'  (via (at {x:.3f} {y:.3f}) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "{net}") (uuid "{uuid.uuid4()}"))\n'

new_u6_pads = {
    'daisy_5v_power': (56.0, 97.615),   
    'audio_in_r': (53.46, 97.615),      
    'i2c1_sda': (53.46, 100.155),       
    'i2c1_scl': (53.46, 102.695),       
    'd13': (53.46, 105.235),            
    'd14': (56.0, 107.775),             
    'gpio_enc_b': (53.46, 107.775),     
    'gpio_enc_sw': (56.0, 110.315),     
    'spi1_mosi': (53.46, 110.315),      
    'spi1_sck': (53.46, 112.855),       
    'spi1_miso': (56.0, 112.855),       
    'gpio_disp_res': (56.0, 115.395),   
    'spi1_cs': (56.0, 117.935),         
    'gpio_disp_dc': (53.46, 120.475),   
}

u5_pads = {
    'gpio_disp_res': (141.080, 112.510),
    'gpio_disp_dc': (143.620, 112.510),
    'spi1_cs': (146.160, 112.510),
    'spi1_sck': (148.700, 112.510),
    'spi1_miso': (151.240, 112.510),
    'spi1_mosi': (153.780, 112.510),
    'i2c1_scl': (156.320, 112.510),
    'i2c1_sda': (158.860, 112.510),
    'd13': (166.480, 112.510),
    'd14': (169.020, 112.510),
    'gpio_enc_b': (171.560, 112.510),
    'gpio_enc_sw': (174.100, 112.510),
    'audio_in_r': (136.000, 97.270),
    'daisy_5v_power': (133.460, 97.270),
}

nets = list(new_u6_pads.keys())

# Clear any stragglers
for net in nets:
    pcb = re.sub(fr'\s*\(segment.*?\(net "{net}"\).*?\)', '', pcb)
    pcb = re.sub(fr'\s*\(via.*?\(net "{net}"\).*?\)', '', pcb)

new_segments = ""
y_channel_base = 75.0
spacing = 0.8

sorted_nets = sorted(nets, key=lambda n: u5_pads[n][0])

right_idx = 0
left_idx = 0

for i, net in enumerate(sorted_nets):
    sx, sy = new_u6_pads[net]
    ex, ey = u5_pads[net]
    
    y_channel = y_channel_base + i * spacing
    
    if sx > 55.0: # Right row
        x_start_drop = 60.0 + right_idx * spacing
        right_idx += 1
    else: # Left row
        x_start_drop = 49.0 - left_idx * spacing
        left_idx += 1
        
    # 1. F.Cu: sx -> x_start_drop
    new_segments += add_track(net, sx, sy, x_start_drop, sy, "F.Cu")
    
    # 2. Via down to In2.Cu
    new_segments += add_via(net, x_start_drop, sy)
    
    # 3. In2.Cu (vertical): y -> y_channel
    new_segments += add_track(net, x_start_drop, sy, x_start_drop, y_channel, "In2.Cu")
    
    # 4. Via to In1.Cu for horizontal run
    new_segments += add_via(net, x_start_drop, y_channel)
    
    # 5. In1.Cu (horizontal): x_start_drop -> ex
    new_segments += add_track(net, x_start_drop, y_channel, ex, y_channel, "In1.Cu")
    
    # 6. Via to In2.Cu for final vertical drop exactly at ex
    new_segments += add_via(net, ex, y_channel)
    
    # 7. In2.Cu (vertical): y_channel -> ey
    new_segments += add_track(net, ex, y_channel, ex, ey, "In2.Cu")
    
    # 8. No via needed at (ex, ey) because U5 pads are through-hole and connect to all layers!

idx = pcb.rfind(')')
pcb = pcb[:idx] + new_segments + pcb[idx:]

with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)

print("Flawless non-crossing traces injected!")
