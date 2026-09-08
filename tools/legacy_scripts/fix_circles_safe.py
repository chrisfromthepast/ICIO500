import re

with open('build/icio500/faceplate_front.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# We need to find (gr_circle ... ) blocks exactly
def replace_circle(match):
    block = match.group(0)
    # Check if this block actually has (end 0 0)
    if '(end 0 0)' not in block:
        return block
        
    center_match = re.search(r'\(center ([0-9.-]+) ([0-9.-]+)\)', block)
    if not center_match:
        return block
        
    cx = float(center_match.group(1))
    cy = float(center_match.group(2))
    
    # If it's the encoder hole at 109.35, it shouldn't have (end 0 0).
    # Wait, the encoder hole is (end 22.55 109.35) so it won't match (end 0 0).
    # Any other (end 0 0) in a gr_circle gets replaced with radius 1.5
    radius = 1.5
    
    # Check if it's the 113.1 hole
    if abs(cy - 113.1) < 0.1:
        radius = 1.5
        
    new_end_x = cx + radius
    new_end_y = cy
    
    return block.replace('(end 0 0)', f'(end {new_end_x:.2f} {new_end_y:.2f})')

# A regex that matches a single gr_circle block safely
# It matches (gr_circle followed by anything that is NOT a (gr_ sequence until the closing parenthesis
# Actually, since KiCad blocks are well-nested, we can just split by '(gr_circle' and re-assemble
parts = pcb.split('(gr_circle')
new_parts = [parts[0]]

for part in parts[1:]:
    # Find the matching closing parenthesis for the block. 
    # Since it's indented, we can just look for the next '\n\t)'
    idx = part.find('\n\t)')
    if idx != -1:
        block_content = part[:idx+3]
        rest = part[idx+3:]
        
        # reconstruct the block
        block = '(gr_circle' + block_content
        new_block = replace_circle(re.match(r'.*', block, re.DOTALL)) # dummy match object not needed
        # Wait, I didn't pass a match object in my logic above. Let's adjust it!
        
        # Actually I can just do:
        if '(end 0 0)' in block_content:
            center_match = re.search(r'\(center ([0-9.-]+) ([0-9.-]+)\)', block_content)
            if center_match:
                cx = float(center_match.group(1))
                cy = float(center_match.group(2))
                radius = 1.5
                if abs(cy - 113.1) < 0.1:
                    radius = 1.5
                new_end_x = cx + radius
                new_end_y = cy
                block_content = block_content.replace('(end 0 0)', f'(end {new_end_x:.2f} {new_end_y:.2f})')
        
        new_parts.append(block_content + rest)
    else:
        new_parts.append(part)

new_pcb = '(gr_circle'.join(new_parts)

with open('build/icio500/faceplate_front.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(new_pcb)
print("Safely fixed gr_circle (end 0 0)")
