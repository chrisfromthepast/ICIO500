import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

nets = [
    'daisy_5v_power', 'audio_in_r', 'i2c1_sda', 'i2c1_scl', 'd13', 'd14',
    'gpio_enc_b', 'gpio_enc_sw', 'spi1_mosi', 'spi1_miso', 'spi1_sck',
    'spi1_cs', 'gpio_disp_dc', 'gpio_disp_res'
]

# A pad is everything from (pad to the matching closing paren, but regex can be tricky with nested parens.
# We can just split the file by "(pad " and then find the first closing net match!

chunks = pcb.split('(pad "')
for i, chunk in enumerate(chunks):
    if i == 0: continue
    
    # Check if this pad chunk contains one of our nets
    net_match = re.search(r'\(net\s+\d+\s+"([^"]+)"\)', chunk)
    if not net_match:
        continue
        
    net_name = net_match.group(1)
    if net_name in nets:
        # Extract at
        at_match = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)', chunk)
        if at_match:
            x = float(at_match.group(1))
            y = float(at_match.group(2))
            
            # Filter out U6 pads
            if abs(x - 56.0) > 3.0 and abs(x - 53.46) > 3.0:
                print(f"{net_name}: {x}, {y}")
