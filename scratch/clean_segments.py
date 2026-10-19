import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    c = f.read()

# Let's count all segments for target nets
target_nets = {
    'gpio_disp_res', 'gpio_disp_dc', 'spi1_cs', 'spi1_sck', 'spi1_miso', 'spi1_mosi',
    'i2c1_scl', 'i2c1_sda', 'd13', 'd14', 'gpio_enc_b', 'gpio_enc_sw',
    'audio_in_r', 'daisy_audio_in', 'audio_in_from_daisy_plus'
}

count = 0
for m in re.finditer(r'\(segment[\s\S]*?\(net\s+"([^"]+)"\)[\s\S]*?\)', c):
    net = m.group(1)
    if net in target_nets:
        count += 1

print(f"Total segments currently in file for target nets: {count}")
