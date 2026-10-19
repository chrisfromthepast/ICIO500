import re
import uuid
import shutil
import subprocess

pcb_file = 'build/icio500/icio500.kicad_pcb'
shutil.copy(pcb_file, 'build/icio500/icio500.kicad_pcb.bak')

with open(pcb_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update U5 footprint:
# Locate U5
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
# Text: (gr_text "DIGITAL" ... (at 127.873162 103.2775 ...))
content = re.sub(r'\(gr_text\s+"DIGITAL"[\s\S]*?\(at\s+[\d\.-]+\s+[\d\.-]+', '(gr_text "DIGITAL"\n\t\t(at 102.62 86', content)
# Rect: (gr_rect (start 78.373162 101.796068) (end 135.373162 143.085)
content = re.sub(r'\(gr_rect\s+\(start\s+78\.373162\s+101\.796068\)\s+\(end\s+135\.373162\s+143\.085\)', '(gr_rect (start 89.0 84.0) (end 116.0 144.0)', content)

# 3. Rip up all old segments and vias for U5 nets:
u5_nets = [
    'gpio_disp_res', 'gpio_disp_dc', 'spi1_cs', 'spi1_sck', 'spi1_miso', 'spi1_mosi',
    'i2c1_scl', 'i2c1_sda', 'd13', 'd14', 'gpio_enc_b', 'gpio_enc_sw',
    'audio_in_r', 'daisy_audio_in', 'audio_in_from_daisy_plus', 'audio_out_r'
]

# Note: for daisy_5v_power, only rip up tracks/vias between X=50 and X=135!
# Remove segments for u5_nets
for net in u5_nets:
    pattern = r'\s*\(segment\s+\(start\s+[\d\.-]+\s+[\d\.-]+\)\s+\(end\s+[\d\.-]+\s+[\d\.-]+\)\s+\(width\s+[\d\.-]+\)\s+\(layer\s+"[^"]+"\)\s+\(net\s+"' + net + r'"\)\s*(?:\(uuid\s+"[^"]+"\)\s*)?\)'
    content = re.sub(pattern, '', content)

# Remove vias for u5_nets
for net in u5_nets:
    pattern = r'\s*\(via\s+\(at\s+[\d\.-]+\s+[\d\.-]+\)\s+\(size\s+[\d\.-]+\)\s+\(drill\s+[\d\.-]+\)\s+\(layers\s+"[^"]+"\s+"[^"]+"\)\s+\(net\s+"' + net + r'"\)\s*(?:\(uuid\s+"[^"]+"\)\s*)?\)'
    content = re.sub(pattern, '', content)

# Also remove old segments for daisy_5v_power that connect to U6/U5 (X < 135)
def keep_pwr_segment(m):
    # check start and end X
    txt = m.group(0)
    pts = re.findall(r'\(start\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(end\s+([\d\.-]+)\s+([\d\.-]+)\)', txt)
    if pts:
        x1, y1, x2, y2 = [float(v) for v in pts[0]]
        if max(x1, x2) < 135.0:
            return '' # remove
    return txt

content = re.sub(r'\s*\(segment[^\)]*\(net\s+"daisy_5v_power"\)[^\)]*\)', keep_pwr_segment, content)

# 4. Generate new zero-via tracks
from test_autoroute import true_routed_results
from route_remaining_u5 import s_audio_in, s_pwr, s_plus

def make_track(p1, p2, layer, net, width=0.25):
    u = str(uuid.uuid4())
    return f'''\t(segment
\t\t(start {p1[0]} {p1[1]})
\t\t(end {p2[0]} {p2[1]})
\t\t(width {width})
\t\t(layer "{layer}")
\t\t(net "{net}")
\t\t(uuid "{u}")
\t)\n'''

new_tracks_str = ""
for name, (pts, layer_num) in true_routed_results.items():
    layer = "F.Cu" if layer_num == 0 else "B.Cu"
    width = 0.5 if name == 'daisy_5v_power' else 0.25
    for i in range(len(pts) - 1):
        new_tracks_str += make_track(pts[i], pts[i+1], layer, name, width=width)


# Remaining 3 nets:
for i in range(len(s_audio_in) - 1):
    new_tracks_str += make_track(s_audio_in[i], s_audio_in[i+1], "F.Cu", "daisy_audio_in", width=0.25)

for i in range(len(s_pwr) - 1):
    new_tracks_str += make_track(s_pwr[i], s_pwr[i+1], "F.Cu", "daisy_5v_power", width=0.5)

for i in range(len(s_plus) - 1):
    new_tracks_str += make_track(s_plus[i], s_plus[i+1], "B.Cu", "audio_in_from_daisy_plus", width=0.25)

# Insert before final ')'
last_paren = content.rfind(')')
content = content[:last_paren] + new_tracks_str + '\n)'

with open(pcb_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied PCB modifications! Zero vias used for all 17 nets.")
