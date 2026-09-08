import re
import uuid

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

pcb = re.sub(r'\(at 52\.17 103\.825 180\)', r'(at 56.0 103.825 180)', pcb)

# The pads for U6 are horizontally aligned.
# At X=56.0, Y is 103.825, rotated 180.
# The 10 rows of pins are at 2.54mm pitch.
# Y ranges from 103.825 - 11.43 to 103.825 + 11.43
# Let's just create 20 tracks for ALL nets? No, we need net codes.
# Since we don't know the net codes without parsing, I can just grep the file for U6 pads!
pads = re.findall(r'\(pad "(.*?)" thru_hole .*? \(at (.*?) (.*?)\) .*? \(net (\d+) "(.*?)"\)', pcb)
# wait, the pad coordinates in the file are RELATIVE to the footprint!
# U6 is rotated 180.
# Relative X=0 -> Absolute X=56.0 (since rotated 180, it's 56.0 - 0 = 56.0)
# Relative X=2.54 -> Absolute X=56.0 - 2.54 = 53.46.

segments = []
for p in pads:
    if p[0].isdigit(): # it's a pin number
        # check if it belongs to U6 by seeing if it's right after U6?
        # Too hard with regex. Let's just look for the block.
        pass

# Actually, I have the exact net codes from the autorouter output from earlier!
# U6 pad 1 (daisy_5v_power)
# U6 pad 2 (audio_in_r)
# ... etc.

