import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Find U6 footprint
idx = pcb.find('Reference" "U6"')
start = pcb.rfind('(footprint', 0, idx)
end = pcb.find(')\n  )', idx) + 4
u6_text = pcb[start:end]

# We want to renumber the pads.
# Old 1 -> 19
# Old 2 -> 20
# Old 19 -> 1
# Old 20 -> 2
# But wait, if we just regex replace `(pad "X"`, we might have collisions!
# So we first replace them with temporary names, then final names.

def get_new_pad(old_str):
    old = int(old_str)
    if old % 2 != 0:
        return str(20 - old)
    else:
        return str(22 - old)

# Find all pads in U6
pads = re.findall(r'\(pad\s+"(\d+)"([^)]+\(at[^)]+\).*?\(net\s+\d+\s+"([^"]+)"\).*?)\)', u6_text, re.DOTALL)
# Wait, some pads might not have nets!
pads = re.findall(r'\(pad\s+"(\d+)"(.*?)\)', u6_text, re.DOTALL)

# Let's map old pad number to its new name AND its new net?
# Wait! If we change the pad name, we must also change the net that is attached to it!
# Because if Pad 19 becomes Pad 1, it should now carry the net that was previously on Pad 1!
# Let's extract the net for each old pad.
old_nets = {}
for p in pads:
    old_num = p[0]
    content = p[1]
    m = re.search(r'\(net\s+(\d+)\s+"([^"]+)"\)', content)
    if m:
        old_nets[old_num] = m.group(0) # e.g. '(net 45 "daisy_5v_power")'

new_u6_text = u6_text
for old_num, content in pads:
    new_num = get_new_pad(old_num)
    # The net that SHOULD be on this physical location is the net that was previously on old_num?
    # NO! If physical location was Pad 19, it becomes Pad 1.
    # The net that should be on New Pad 1 is the net that was previously on Old Pad 1!
    # Because Old Pad 1 had `daisy_5v_power` (which logically belongs to Pad 1).
    # So physical location (previously 19) gets New Pad 1 AND Old Pad 1's net!
    
    # Let's construct the new pad block.
    # We replace `(pad "old_num"` with `(pad "TEMP_new_num"`
    temp_pad = f'(pad "TEMP_{new_num}"'
    
    # We replace the net inside this pad's content with the net from the OLD pad number that corresponds to new_num?
    # Wait: Physical location X was Old Pad 19.
    # New pad number for X is 1.
    # The net that belongs to New Pad 1 is old_nets["1"].
    # So we replace whatever net is in X's content with old_nets["1"].
    
    new_content = content
    # remove existing net
    new_content = re.sub(r'\s*\(net\s+\d+\s+"[^"]+"\)', '', new_content)
    
    # add the correct net
    correct_net = old_nets.get(new_num)
    if correct_net:
        # insert before the closing paren of the pad?
        # actually, the regex above captured everything EXCEPT the closing paren of the pad.
        new_content += f' {correct_net}'
        
    # Replace in u6_text
    # We must match exactly this pad
    old_pad_full = f'(pad "{old_num}"{content})'
    new_pad_full = f'{temp_pad}{new_content})'
    new_u6_text = new_u6_text.replace(old_pad_full, new_pad_full)

# Now remove "TEMP_"
new_u6_text = new_u6_text.replace('(pad "TEMP_', '(pad "')

# Replace U6 in PCB
pcb = pcb[:start] + new_u6_text + pcb[end:]

# Next, we want to RIP UP ALL TRACES connected to these nets in the routing area!
# The nets are:
routing_nets = [
    'daisy_5v_power', 'audio_in_r', 'i2c1_sda', 'i2c1_scl', 'd13', 'd14',
    'gpio_enc_b', 'gpio_enc_sw', 'spi1_mosi', 'spi1_miso', 'spi1_sck',
    'spi1_cs', 'gpio_disp_dc', 'gpio_disp_res'
]

# We will just rip up ALL segments and vias for these nets. The user deleted them anyway.
# We will then use FreeRouting to route the board! It will route everything flawlessly!
# Or we can just use KiCad's Python FreeRouting wrapper? No.

# Let's just delete the segments.
segments = re.findall(r'(\s*\(segment.*?\))', pcb, re.DOTALL)
vias = re.findall(r'(\s*\(via.*?\))', pcb, re.DOTALL)

removed_segs = 0
for seg in segments:
    m = re.search(r'\(net\s+\d+\s+"([^"]+)"\)', seg)
    if m and m.group(1) in routing_nets:
        pcb = pcb.replace(seg, '')
        removed_segs += 1

removed_vias = 0
for via in vias:
    m = re.search(r'\(net\s+\d+\s+"([^"]+)"\)', via)
    if m and m.group(1) in routing_nets:
        pcb = pcb.replace(via, '')
        removed_vias += 1

with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)

print(f"Renumbered U6 and updated nets. Removed {removed_segs} segments and {removed_vias} vias.")
