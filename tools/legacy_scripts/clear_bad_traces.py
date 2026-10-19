import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

nets_to_clear = [
    'daisy_5v_power', 'audio_in_r', 'i2c1_sda', 'i2c1_scl', 'd13', 'd14',
    'gpio_enc_b', 'gpio_enc_sw', 'spi1_mosi', 'spi1_sck', 'spi1_miso',
    'gpio_disp_res', 'spi1_cs', 'gpio_disp_dc'
]

# Remove my injected UUID traces
for net in nets_to_clear:
    pcb = re.sub(fr'\s*\(segment.*?\(net "{net}"\).*?\)', '', pcb)
    pcb = re.sub(fr'\s*\(via.*?\(net "{net}"\).*?\)', '', pcb)

with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)

print("Cleared bad traces!")
