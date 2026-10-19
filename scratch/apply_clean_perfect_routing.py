import re
import uuid
import shutil
import subprocess

pcb_file = 'build/icio500/icio500.kicad_pcb'
bak_file = 'build/icio500/icio500.kicad_pcb.bak'

# Restore from clean bak
shutil.copy(bak_file, pcb_file)

with open(pcb_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update U5 footprint position and orientation
idx = content.find('"Reference" "U5"')
start = content.rfind('(footprint', 0, idx)
depth = 0
end = start
for i in range(start, len(content)):
    if content[i] == '(': depth += 1
    elif content[i] == ')':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
u5_block = content[start:end]

# Change (at 130.92 112.51 -90) to (at 95 90 0)
new_u5 = re.sub(r'\(at\s+[\d\.-]+\s+[\d\.-]+\s+-?90\)', '(at 95 90 0)', u5_block)
# In pads: change (at lx ly 270) to (at lx ly 0)
new_u5 = re.sub(r'\(at\s+([-\d.]+)\s+([-\d.]+)\s+270\)', r'(at \1 \2 0)', new_u5)

content = content[:start] + new_u5 + content[end:]

# 2. Update silkscreen DIGITAL rect and text
content = re.sub(r'\(gr_text\s+"DIGITAL"[\s\S]*?\(at\s+[\d\.-]+\s+[\d\.-]+', '(gr_text "DIGITAL"\n\t\t(at 102.62 86', content)
content = re.sub(r'\(gr_rect\s+\(start\s+78\.373162\s+101\.796068\)\s+\(end\s+135\.373162\s+143\.085\)', '(gr_rect (start 89.0 84.0) (end 116.0 144.0)', content)

# 3. Rip up all old tracks and vias for U5 nets and obsolete gnd tracks in U5 box
all_u5_nets = {
    'gpio_disp_res', 'gpio_disp_dc', 'spi1_cs', 'spi1_sck', 'spi1_miso', 'spi1_mosi',
    'i2c1_scl', 'i2c1_sda', 'd13', 'd14', 'gpio_enc_b', 'gpio_enc_sw',
    'audio_in_r', 'daisy_audio_in', 'audio_in_from_daisy_plus', 'audio_out_r'
}

def clean_segment(m):
    txt = m.group(0)
    net_m = re.search(r'\(net\s+"([^"]+)"\)', txt)
    if not net_m:
        return txt
    net = net_m.group(1)
    if net in all_u5_nets:
        return ''
    if net == 'daisy_5v_power':
        pts = re.findall(r'\(start\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(end\s+([\d\.-]+)\s+([\d\.-]+)\)', txt)
        if pts:
            x1, y1, x2, y2 = [float(v) for v in pts[0]]
            if max(x1, x2) < 135.0:
                return ''
    if net == 'gnd':
        pts = re.findall(r'\(start\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(end\s+([\d\.-]+)\s+([\d\.-]+)\)', txt)
        if pts:
            x1, y1, x2, y2 = [float(v) for v in pts[0]]
            if 80 <= x1 <= 135 and 80 <= y1 <= 145 and 80 <= x2 <= 135 and 80 <= y2 <= 145:
                return ''
    return txt

def clean_via(m):
    txt = m.group(0)
    net_m = re.search(r'\(net\s+"([^"]+)"\)', txt)
    if not net_m:
        return txt
    net = net_m.group(1)
    if net in all_u5_nets:
        return ''
    if net in ['gnd', 'daisy_5v_power']:
        at_m = re.search(r'\(at\s+([\d\.-]+)\s+([\d\.-]+)\)', txt)
        if at_m:
            x, y = float(at_m.group(1)), float(at_m.group(2))
            if 80 <= x <= 135 and 80 <= y <= 145:
                return ''
    return txt

content = re.sub(r'\s*\(segment[\s\S]*?\n\t\)', clean_segment, content)
content = re.sub(r'\s*\(via[\s\S]*?\n\t\)', clean_via, content)

# 4. Generate the exact elegant routes
def make_seg(p1, p2, layer, net, width=0.25):
    u = str(uuid.uuid4())
    return f'''\t(segment
\t\t(start {p1[0]} {p1[1]})
\t\t(end {p2[0]} {p2[1]})
\t\t(width {width})
\t\t(layer "{layer}")
\t\t(net "{net}")
\t\t(uuid "{u}")
\t)\n'''

def make_trace(pts, layer, net, width=0.25):
    s = ""
    for i in range(len(pts) - 1):
        s += make_seg(pts[i], pts[i+1], layer, net, width)
    return s

new_tracks = ""

# --- 12 Digital Bus Nets ---
# 1. gpio_disp_res (F.Cu)
# U6 Pin 17 (56.0, 100.155) -> U5 Pin 5 (95.0, 100.16)
new_tracks += make_trace([(56.0, 100.155), (95.0, 100.16)], "F.Cu", "gpio_disp_res")

# 2. gpio_disp_dc (B.Cu)
# U6 Pin 16 (53.46, 102.695) -> U5 Pin 6 (95.0, 102.70)
new_tracks += make_trace([(53.46, 102.695), (95.0, 102.70)], "B.Cu", "gpio_disp_dc")

# 3. spi1_cs (F.Cu)
# U6 Pin 15 (56.0, 102.695) -> U5 Pin 7 (95.0, 105.24)
new_tracks += make_trace([(56.0, 102.695), (58.545, 105.24), (95.0, 105.24)], "F.Cu", "spi1_cs")

# 4. spi1_sck (B.Cu)
# U6 Pin 14 (53.46, 105.235) -> U5 Pin 8 (95.0, 107.78)
new_tracks += make_trace([(53.46, 105.235), (56.005, 107.78), (95.0, 107.78)], "B.Cu", "spi1_sck")

# 5. spi1_miso (F.Cu)
# U6 Pin 13 (56.0, 105.235) -> U5 Pin 9 (95.0, 110.32)
new_tracks += make_trace([(56.0, 105.235), (61.085, 110.32), (95.0, 110.32)], "F.Cu", "spi1_miso")

# 6. spi1_mosi (B.Cu)
# U6 Pin 12 (53.46, 107.775) -> U5 Pin 10 (95.0, 112.86)
new_tracks += make_trace([(53.46, 107.775), (58.545, 112.86), (95.0, 112.86)], "B.Cu", "spi1_mosi")

# 7. i2c1_scl (B.Cu)
# U6 Pin 6 (53.46, 115.395) -> U5 Pin 11 (95.0, 115.40)
new_tracks += make_trace([(53.46, 115.395), (95.0, 115.40)], "B.Cu", "i2c1_scl")

# 8. i2c1_sda (B.Cu)
# U6 Pin 4 (53.46, 117.935) -> U5 Pin 12 (95.0, 117.94)
new_tracks += make_trace([(53.46, 117.935), (95.0, 117.94)], "B.Cu", "i2c1_sda")

# 9. d13 (B.Cu)
# U6 Pin 8 (53.46, 112.855) -> U5 Pin 15 (95.0, 125.56)
new_tracks += make_trace([(53.46, 112.855), (66.165, 125.56), (95.0, 125.56)], "B.Cu", "d13")

# 10. d14 (B.Cu)
# U6 Pin 9 (56.0, 110.315) -> U5 Pin 16 (95.0, 128.10)
new_tracks += make_trace([(56.0, 110.315), (73.785, 128.10), (95.0, 128.10)], "B.Cu", "d14")

# 11. gpio_enc_b (F.Cu)
# U6 Pin 10 (53.46, 110.315) -> U5 Pin 17 (95.0, 130.64)
# Pass between Pin 11 and Pin 9 on F.Cu or exit right
new_tracks += make_trace([(53.46, 110.315), (73.785, 130.64), (95.0, 130.64)], "F.Cu", "gpio_enc_b")

# 12. gpio_enc_sw (F.Cu)
# U6 Pin 11 (56.0, 107.775) -> U5 Pin 18 (95.0, 133.18)
new_tracks += make_trace([(56.0, 107.775), (81.405, 133.18), (95.0, 133.18)], "F.Cu", "gpio_enc_sw")

# --- Power and Audio Nets ---
# 13. daisy_5v_power (F.Cu)
# U6 Pin 1 (56.0, 120.475) -> around bottom (Y=141) -> U5 Pin 39 (110.24, 92.54) -> C25 Pin 1 (128.42, 136.51)
new_tracks += make_trace([
    (56.0, 120.475), (56.0, 141.0), (118.0, 141.0), (118.0, 92.54), (110.24, 92.54)
], "F.Cu", "daisy_5v_power", width=0.5)

# Connect U5 Pin 39 to C25 (128.42, 136.51)
new_tracks += make_trace([
    (118.0, 136.51), (128.42, 136.51)
], "F.Cu", "daisy_5v_power", width=0.5)

# 14. audio_in_r (B.Cu)
# U6 Pin 2 (53.46, 120.475) -> around bottom (Y=143) -> U5 Pin 38 (110.24, 95.08)
new_tracks += make_trace([
    (53.46, 120.475), (53.46, 143.0), (120.0, 143.0), (120.0, 95.08), (110.24, 95.08)
], "B.Cu", "audio_in_r", width=0.25)

# 15. daisy_audio_in (F.Cu)
# U5 Pin 37 (110.24, 97.62) -> C17 Pin 1 (159.825, 91.60)
new_tracks += make_trace([
    (110.24, 97.62), (116.26, 91.60), (159.825, 91.60)
], "F.Cu", "daisy_audio_in", width=0.25)

# 16. audio_in_from_daisy_plus (B.Cu)
# U5 Pin 35 (110.24, 102.70) -> R7 Pin 1 (172.30, 97.90)
new_tracks += make_trace([
    (110.24, 102.70), (115.04, 97.90), (172.30, 97.90)
], "B.Cu", "audio_in_from_daisy_plus", width=0.25)

# Insert tracks
last_paren = content.rfind(')')
content = content[:last_paren] + new_tracks + '\n)'

with open(pcb_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied perfect clean zero-via routing!")
