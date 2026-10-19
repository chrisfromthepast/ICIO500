import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    c = f.read()

# Find all nets on U5
u5_nets = [
    'gpio_disp_res', 'gpio_disp_dc', 'spi1_cs', 'spi1_sck', 'spi1_miso', 'spi1_mosi',
    'i2c1_scl', 'i2c1_sda', 'd13', 'd14', 'gpio_enc_b', 'gpio_enc_sw',
    'audio_in_from_daisy_plus', 'audio_out_r', 'daisy_audio_in', 'audio_in_r', 'daisy_5v_power', 'gnd'
]

tracks_by_net = {net: [] for net in u5_nets}
vias_by_net = {net: [] for net in u5_nets}

for m in re.finditer(r'\(segment\s+\(start\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(end\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(width\s+([\d\.-]+)\)\s+\(layer\s+"([^"]+)"\)\s+\(net\s+"([^"]+)"\)', c):
    nname = m.group(7)
    if nname in tracks_by_net:
        tracks_by_net[nname].append((float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(6)))

for m in re.finditer(r'\(via\s+\(at\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(size\s+[\d\.-]+\)\s+\(drill\s+[\d\.-]+\)\s+\(layers\s+"[^"]+"\s+"[^"]+"\)\s+\(net\s+"([^"]+)"\)', c):
    nname = m.group(3)
    if nname in vias_by_net:
        vias_by_net[nname].append((float(m.group(1)), float(m.group(2))))

print("Existing tracks and vias for U5 nets:")
for net in u5_nets:
    print(f"  {net:25s}: {len(tracks_by_net[net]):2d} segments, {len(vias_by_net[net]):2d} vias")


print("Existing tracks for U5 nets:")
for net, segs in tracks_by_net.items():
    print(f"  {net:25s}: {len(segs)} segments")
