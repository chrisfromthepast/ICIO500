import re
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Extract all pads
pad_blocks = re.findall(r'(\(pad.*?^\s*\))', pcb, re.MULTILINE | re.DOTALL)
if not pad_blocks:
    # Try simpler matching
    pad_blocks = re.findall(r'\(pad\s+"[^"]+".*?\(net\s+\d+\s+"[^"]+"\).*?\)', pcb, re.DOTALL)

for b in pad_blocks:
    m_net = re.search(r'\(net\s+\d+\s+"([^"]+)"\)', b)
    if m_net:
        net = m_net.group(1)
        m_at = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)', b)
        if m_at:
            x, y = m_at.groups()
            if abs(float(x) - 56.0) > 3.0 and abs(float(x) - 53.46) > 3.0:
                print(f'{net} at {x}, {y}')
