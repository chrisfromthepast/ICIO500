import re
import uuid
import subprocess

subprocess.run(['git', 'checkout', 'a2b0777', 'build/icio500/icio500.kicad_pcb'])

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

pcb = re.sub(r'\(at 52\.17 120\.475 180\)', r'(at 56.0 120.475 180)', pcb)

new_segments = []
def add_segment(sx, sy, ex, ey, layer, net_name):
    uid = str(uuid.uuid4())
    seg = f'\n  (segment\n    (start {sx:.4f} {sy:.4f})\n    (end {ex:.4f} {ey:.4f})\n    (width 0.25)\n    (layer "{layer}")\n    (net "{net_name}")\n    (uuid "{uid}")\n  )'
    new_segments.append(seg)

def add_via(x, y, net_name):
    uid = str(uuid.uuid4())
    via = f'\n  (via\n    (at {x:.4f} {y:.4f})\n    (size 0.8)\n    (drill 0.4)\n    (layers "F.Cu" "B.Cu")\n    (net "{net_name}")\n    (uuid "{uid}")\n  )'
    new_segments.append(via)

# F.Cu: i2c1_sda
add_segment(53.46, 117.935, 95.91, 117.935, "F.Cu", "i2c1_sda")
add_segment(95.91, 117.935, 95.91, 104.46, "F.Cu", "i2c1_sda")

# B.Cu: d13
add_segment(53.46, 112.855, 95.4, 112.855, "B.Cu", "d13")
add_segment(95.4, 112.855, 95.4, 112.5, "B.Cu", "d13")

# In2.Cu traces: daisy_5v_power, gpio_enc_sw, gpio_disp_dc, audio_in_r, i2c1_scl, spi1_cs, gpio_disp_res
# daisy_5v_power (Pad 1, Y=120.475 -> 112.0)
add_segment(56.0, 120.475, 86.5, 120.475, "In2.Cu", "daisy_5v_power")
add_segment(86.5, 120.475, 86.5, 112.0, "In2.Cu", "daisy_5v_power")

# audio_in_r (Pad 2, Y=120.475 -> 104.46). Shift Y to 121.0 to avoid daisy
add_segment(53.46, 120.475, 53.46, 121.0, "In2.Cu", "audio_in_r")
add_segment(53.46, 121.0, 93.37, 121.0, "In2.Cu", "audio_in_r")
add_segment(93.37, 121.0, 93.37, 104.46, "In2.Cu", "audio_in_r")
add_via(93.37, 104.46, "audio_in_r")

# i2c1_scl (Pad 6, Y=115.395 -> 104.46)
add_segment(53.46, 115.395, 98.45, 115.395, "In2.Cu", "i2c1_scl")
add_segment(98.45, 115.395, 98.45, 104.46, "In2.Cu", "i2c1_scl")
add_via(98.45, 104.46, "i2c1_scl")

# gpio_enc_sw (Pad 12, Y=107.775 -> 112.5)
add_segment(56.0, 107.775, 87.7, 107.775, "In2.Cu", "gpio_enc_sw")
add_segment(87.7, 107.775, 87.7, 112.5, "In2.Cu", "gpio_enc_sw")

# gpio_disp_dc (Pad 20, Y=102.695 -> 105.73)
add_segment(53.46, 102.695, 112.42, 102.695, "In2.Cu", "gpio_disp_dc")
add_segment(112.42, 102.695, 112.42, 105.73, "In2.Cu", "gpio_disp_dc")

# spi1_cs (Pad 18, Y=102.695 -> 107.00). Shift Y to 102.0 to avoid gpio_disp_dc
add_segment(56.0, 102.695, 56.0, 102.0, "In2.Cu", "spi1_cs")
add_segment(56.0, 102.0, 111.15, 102.0, "In2.Cu", "spi1_cs")
add_segment(111.15, 102.0, 111.15, 107.00, "In2.Cu", "spi1_cs")
add_via(111.15, 107.00, "spi1_cs")

# gpio_disp_res (Pad 17, Y=100.155 -> 107.00)
add_segment(56.0, 100.155, 113.69, 100.155, "In2.Cu", "gpio_disp_res")
add_segment(113.69, 100.155, 113.69, 107.00, "In2.Cu", "gpio_disp_res")
add_via(113.69, 107.00, "gpio_disp_res")

# In1.Cu traces: d14, gpio_enc_b, spi1_mosi, spi1_miso, spi1_sck
# d14 (Pad 9, Y=110.315 -> 112.5)
add_segment(56.0, 110.315, 92.8, 110.315, "In1.Cu", "d14")
add_segment(92.8, 110.315, 92.8, 112.5, "In1.Cu", "d14")

# gpio_enc_b (Pad 11, Y=110.315 -> 112.5). Shift Y to 109.5 to avoid d14
add_segment(53.46, 110.315, 53.46, 109.5, "In1.Cu", "gpio_enc_b")
add_segment(53.46, 109.5, 90.3, 109.5, "In1.Cu", "gpio_enc_b")
add_segment(90.3, 109.5, 90.3, 112.5, "In1.Cu", "gpio_enc_b")

# spi1_mosi (Pad 13, Y=107.775 -> 104.46)
add_segment(53.46, 107.775, 106.07, 107.775, "In1.Cu", "spi1_mosi")
add_segment(106.07, 107.775, 106.07, 104.46, "In1.Cu", "spi1_mosi")

# spi1_miso (Pad 16, Y=105.235 -> 107.00)
add_segment(56.0, 105.235, 108.61, 105.235, "In1.Cu", "spi1_miso")
add_segment(108.61, 105.235, 108.61, 107.00, "In1.Cu", "spi1_miso")

# spi1_sck (Pad 15, Y=105.235 -> 105.73). Shift Y to 104.5 to avoid spi1_miso
add_segment(53.46, 105.235, 53.46, 104.5, "In1.Cu", "spi1_sck")
add_segment(53.46, 104.5, 109.88, 104.5, "In1.Cu", "spi1_sck")
add_segment(109.88, 104.5, 109.88, 105.73, "In1.Cu", "spi1_sck")

# GND vias for U6
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
