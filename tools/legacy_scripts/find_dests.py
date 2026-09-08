import re
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

nets = [
    'daisy_5v_power', 'audio_in_r', 'i2c1_sda', 'i2c1_scl', 'd13', 'd14',
    'gpio_enc_b', 'gpio_enc_sw', 'spi1_mosi', 'spi1_miso', 'spi1_sck',
    'spi1_cs', 'gpio_disp_dc', 'gpio_disp_res'
]

# (pad "23" thru_hole circle (at 100.33 118.11) (size 1.524 1.524) (drill 1.016) (layers *.Cu *.Mask) (net 45 "i2c1_sda") (pinfunction "Pin_23") (pintype "passive") (uuid "ee2318ea-4f9e-43b9-a29e-f00e9fcb9cda"))

for net in nets:
    pads = re.findall(fr'\(pad\s+"[^"]+"\s+[^)]+\s+\(at\s+([\d.-]+)\s+([\d.-]+).*?\(net\s+\d+\s+"{net}"\)', pcb)
    dest_pads = []
    for p in pads:
        if abs(float(p[0]) - 56.0) > 5.0 and abs(float(p[0]) - 53.46) > 5.0:
            dest_pads.append(p)
    print(f'{net}: {dest_pads}')
