import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Instead of regex over the whole footprint, we will find `(pad "X"` precisely where it's near U6!
# We know U6 is at 56.0 120.475 180.
# We will just parse the file line by line to extract U6.

lines = pcb.split('\n')
u6_start = -1
u6_end = -1
in_u6 = False
brace_count = 0

for i, line in enumerate(lines):
    if '(footprint "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Horizontal"' in line:
        # Check if the next few lines have Reference "U6"
        for j in range(i, min(i+20, len(lines))):
            if 'Reference" "U6"' in lines[j]:
                u6_start = i
                in_u6 = True
                break
    
    if in_u6:
        brace_count += line.count('(')
        brace_count -= line.count(')')
        if brace_count == 0:
            u6_end = i
            break

if u6_start != -1 and u6_end != -1:
    u6_lines = lines[u6_start:u6_end+1]
    
    # Now we safely rename the pads!
    # First, we need to extract the nets for the OLD pads.
    old_nets = {}
    for j, line in enumerate(u6_lines):
        if '(pad "' in line:
            m_pad = re.search(r'\(pad\s+"(\d+)"', line)
            if m_pad:
                old_num = m_pad.group(1)
                # the net is on the same line in KiCad 10
                m_net = re.search(r'\(net\s+"([^"]+)"\)', line)
                if m_net:
                    old_nets[old_num] = m_net.group(1)
    
    # Now create new lines
    new_u6_lines = []
    for line in u6_lines:
        if '(pad "' in line:
            m_pad = re.search(r'\(pad\s+"(\d+)"', line)
            if m_pad:
                old_num = m_pad.group(1)
                old_int = int(old_num)
                new_num = str(20 - old_int) if old_int % 2 != 0 else str(22 - old_int)
                
                # Replace pad number
                line = re.sub(r'\(pad\s+"\d+"', f'(pad "{new_num}"', line)
                
                # Replace net with the one that belongs to new_num
                target_net = old_nets.get(new_num)
                if target_net:
                    if '(net ' in line:
                        line = re.sub(r'\(net\s+"[^"]+"\)', f'(net "{target_net}")', line)
                    else:
                        line = line.replace(')', f' (net "{target_net}"))')
        new_u6_lines.append(line)
        
    lines[u6_start:u6_end+1] = new_u6_lines
    
    with open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print("U6 renumbered securely!")
else:
    print("Could not parse U6 bounds.")
