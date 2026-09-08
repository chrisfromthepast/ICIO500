import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

def add_track(net, x1, y1, x2, y2, layer="In1.Cu"):
    return f'  (segment (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (width 0.25) (layer "{layer}") (net "{net}"))\n'

def add_via(net, x, y):
    return f'  (via (at {x:.3f} {y:.3f}) (size 0.8) (drill 0.4) (layers "F.Cu" "B.Cu") (net "{net}"))\n'

# Because U6 was renumbered, Pad 1 is now at Y=97.615 (Top of U6).
# Pad 1 logically carries `daisy_5v_power` in main.ato!
# So `daisy_5v_power` starts at 97.615!
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

# Let's remove ALL traces on these nets to start perfectly clean.
for net in nets:
    pcb = re.sub(fr'\s*\(segment.*?\(net "{net}"\)\)', '', pcb)
    pcb = re.sub(fr'\s*\(via.*?\(net "{net}"\)\)', '', pcb)

# We will inject the traces using the new CORRECT mappings.
# Since the mapping is now logically inverted but physically straight, the lines will be beautiful.

new_segments = ""

y_bus_base = 98.0
x_drop_base = 65.0
spacing = 0.5

# Sort nets by U5 X coordinate (right to left? Actually Left to Right)
sorted_nets = sorted(nets, key=lambda n: u5_pads[n][0])

for i, net in enumerate(sorted_nets):
    sx, sy = new_u6_pads[net]
    ex, ey = u5_pads[net]
    
    x_drop = x_drop_base + i * spacing
    y_bus = y_bus_base + i * spacing
    
    # 1. Horizontal from U6 to x_drop on In1.Cu
    new_segments += add_track(net, sx, sy, x_drop, sy, "In1.Cu")
    
    # 2. Via to In2.Cu
    new_segments += add_via(net, x_drop, sy)
    
    # 3. Vertical on In2.Cu to y_bus
    new_segments += add_track(net, x_drop, sy, x_drop, y_bus, "In2.Cu")
    
    # 4. Via back to In1.Cu
    new_segments += add_via(net, x_drop, y_bus)
    
    # 5. Horizontal on In1.Cu to ex
    new_segments += add_track(net, x_drop, y_bus, ex, y_bus, "In1.Cu")
    
    # 6. Via to In2.Cu
    new_segments += add_via(net, ex, y_bus)
    
    # 7. Vertical on In2.Cu to ey
    new_segments += add_track(net, ex, y_bus, ex, ey, "In2.Cu")


idx = pcb.rfind(')')
pcb = pcb[:idx] + new_segments + pcb[idx:]

with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)

print("Beautiful Manhattan routing injected using the NEW U6 coordinates!")
