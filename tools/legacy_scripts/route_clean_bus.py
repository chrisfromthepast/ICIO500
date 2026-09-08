import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# I will write a simple python script to inject the tracks into the kicad file.

def add_track(net, x1, y1, x2, y2, layer="In1.Cu"):
    return f'  (segment (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (width 0.25) (layer "{layer}") (net "{net}"))\n'

def add_via(net, x, y):
    return f'  (via (at {x:.3f} {y:.3f}) (size 0.8) (drill 0.4) (layers "F.Cu" "B.Cu") (net "{net}"))\n'

# We know U6 pads and U5 destinations precisely.
u6_pads = {
    'daisy_5v_power': (56.0, 120.475),   
    'audio_in_r': (53.46, 120.475),      
    'i2c1_sda': (53.46, 117.935),       
    'i2c1_scl': (53.46, 115.395),       
    'd13': (53.46, 112.855),            
    'd14': (56.0, 110.315),             
    'gpio_enc_b': (53.46, 110.315),     
    'gpio_enc_sw': (56.0, 107.775),     
    'spi1_mosi': (53.46, 107.775),      
    'spi1_sck': (53.46, 105.235),       
    'spi1_miso': (56.0, 105.235),       
    'gpio_disp_res': (56.0, 102.695),   
    'spi1_cs': (56.0, 100.155),         
    'gpio_disp_dc': (53.46, 97.615),   
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

# The routing strategy:
# We will route all signals out of U6 to the right on In1.Cu.
# We will assign each net a unique Y-channel for the horizontal run.
# To avoid crossings, we will drop a via to In2.Cu for the vertical segments if they cross!
# Actually, if we just run them out to different X coordinates, then go to the Y channel, they won't cross on the same layer.
# Let's write a simple router.

new_segments = ""

# Delete all old traces in the routing area (X < 130)
# We will use regex to find and remove them.
nets = list(u6_pads.keys())
for net in nets:
    # Remove segments
    pcb = re.sub(fr'\s*\(segment.*?\(net "{net}"\)\)', '', pcb)
    # Remove vias
    pcb = re.sub(fr'\s*\(via.*?\(net "{net}"\)\)', '', pcb)

# Now inject our beautiful routing!
# For simplicity and extreme neatness, we will route:
# U6 (x, y) -> right to X=65 -> via to In2.Cu -> up/down to Y_bus -> via to In1.Cu -> right to X_u5 -> up/down to U5_pad.
# Wait, if we just use a Y-channel for each net on In1.Cu, and X-channels on In2.Cu:
# 1. In1.Cu: U6 to X_drop
# 2. In2.Cu: X_drop to Y_bus
# 3. In1.Cu: Y_bus to U5_X
# 4. In2.Cu: U5_X to U5_Y (which is 112.510)
# Actually, if all horizontal is In1 and all vertical is In2, there are NO collisions!

y_bus_base = 98.0
x_drop_base = 65.0
spacing = 0.5

# Sort nets by U5 X coordinate (right to left)
sorted_nets = sorted(nets, key=lambda n: u5_pads[n][0])

for i, net in enumerate(sorted_nets):
    sx, sy = u6_pads[net]
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
    
    # 6. Via to In2.Cu (unless we can reach it directly? U5 is thru-hole so any layer works)
    new_segments += add_via(net, ex, y_bus)
    
    # 7. Vertical on In2.Cu to ey
    new_segments += add_track(net, ex, y_bus, ex, ey, "In2.Cu")

# Inject segments before the last closing parenthesis of pcb
# Actually, we can just insert them right before the first `(segment` or at the end.
# Just find the end of the file and insert before the last `)`
idx = pcb.rfind(')')
pcb = pcb[:idx] + new_segments + pcb[idx:]

with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)

print("Beautiful Manhattan routing injected!")
