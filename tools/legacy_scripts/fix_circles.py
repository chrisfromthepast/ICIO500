import re

with open('build/icio500/faceplate_front.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Let's find all (gr_circle) blocks with (end 0 0)
def replace_circle(match):
    block = match.group(0)
    # Extract center
    center_match = re.search(r'\(center ([0-9.-]+) ([0-9.-]+)\)', block)
    if not center_match:
        return block
    cx = float(center_match.group(1))
    cy = float(center_match.group(2))
    
    # If it's an LED, radius = 1.5
    # If it's the anti-rotation pin at 113.1, maybe radius = 1.5?
    # Actually, any (end 0 0) is a bug. Let's make radius = 1.5 for all of them!
    # Wait, the encoder hole is at 109.35, and its end is NOT (0 0), it's (22.55 109.35).
    # So all the (end 0 0) ones are either LEDs (radius 1.5) or the anti-rotation pin (radius 1.5 is fine).
    
    radius = 1.5
    new_end_x = cx + radius
    new_end_y = cy
    
    new_block = re.sub(r'\(end 0 0\)', f'(end {new_end_x:.2f} {new_end_y:.2f})', block)
    return new_block

# Use re.sub with a function
new_pcb = re.sub(r'\(gr_circle[\s\S]*?\(end 0 0\)[\s\S]*?\)', replace_circle, pcb)

with open('build/icio500/faceplate_front.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(new_pcb)
print("Fixed (end 0 0) circles!")
