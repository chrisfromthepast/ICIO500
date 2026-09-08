import re
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# U5 is a DIP-40 socket, or maybe Daisy_Seed_Rev4?
# Let's find any pad that matches our nets and is NOT on U6.
nets = [
    'daisy_5v_power', 'audio_in_r', 'i2c1_sda', 'i2c1_scl', 'd13', 'd14',
    'gpio_enc_b', 'gpio_enc_sw', 'spi1_mosi', 'spi1_miso', 'spi1_sck',
    'spi1_cs', 'gpio_disp_dc', 'gpio_disp_res'
]

# We want to know where these nets go.
for net in nets:
    pads = re.findall(fr'\(pad\s+"[^"]+"\s+(?:thru_hole|smd).*?\(at\s+([\d.-]+)\s+([\d.-]+)[^)]*\).*?\(net\s+\d+\s+"{net}"\)', pcb)
    dests = [p for p in pads if abs(float(p[0]) - 56.0) > 2.0 and abs(float(p[0]) - 53.46) > 2.0]
    print(f'{net}: {dests}')
