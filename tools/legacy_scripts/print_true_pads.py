import sys
import pcbnew
import math

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
nets = [
    'daisy_5v_power', 'audio_in_r', 'i2c1_sda', 'i2c1_scl', 'd13', 'd14',
    'gpio_enc_b', 'gpio_enc_sw', 'spi1_mosi', 'spi1_miso', 'spi1_sck',
    'spi1_cs', 'gpio_disp_dc', 'gpio_disp_res'
]

print("=== PADS ===")
for net_name in nets:
    net = board.GetNetsByName().get(net_name)
    if not net:
        continue
    for pad in board.GetPads():
        if pad.GetNetname() == net_name:
            ref = pad.GetParent().GetReference()
            pos = pad.GetPosition()
            print(f"{net_name}: {ref} Pad {pad.GetName()} at {pos.x / 1000000.0}, {pos.y / 1000000.0} (Layer {pad.GetLayerName()})")
