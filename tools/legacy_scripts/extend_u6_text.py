import re
import uuid

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# 1. Move U6
pcb = re.sub(r'\(at 52\.17 103\.825 180\)', r'(at 56.0 103.825 180)', pcb)

# 2. Find U6 pads to create tracks
# Actually, I know exactly where the 20 pads are!
# U6 is a 2x10 right-angle header at Y=103.825, rotated 180.
# The pins are at Y = 103.825 - 9*2.54/2 ... etc.
# Wait, pitch is 2.54. 10 pins in each row.
# But what are the exact Y coordinates?
import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
u6 = board.FindFootprintByReference('U6')

segments = []
for pad in u6.Pads():
    net = pad.GetNetname()
    net_code = pad.GetNetCode()
    if net_code == 0: continue
    
    # After moving to 56.0, pad X is shifted by +3.83
    # Wait, the pcbnew object STILL has it at 52.17!
    px = pad.GetPosition().x / 1e6 + 3.83
    py = pad.GetPosition().y / 1e6
    
    width = 0.4 if net in ['gnd', 'GND', 'v_plus', 'v_minus', 'daisy_5v_power', '+3V3', '+3V3_IN'] else 0.25
    uid = str(uuid.uuid4())
    
    # Track from px-3.83 to px
    seg = f'\n  (segment (start {px-3.83:.4f} {py:.4f}) (end {px:.4f} {py:.4f}) (width {width}) (layer "F.Cu") (net {net_code}) (uuid "{uid}"))'
    segments.append(seg)
    # Also add one on B.Cu just in case? No, F.Cu is fine.

# Append segments
insert_pos = pcb.rfind('\n)')
pcb = pcb[:insert_pos] + ''.join(segments) + pcb[insert_pos:]

with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)
print(f"Moved U6 and added {len(segments)} extension tracks.")
