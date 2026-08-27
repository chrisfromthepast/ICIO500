import re
with open('C:/Program Files/KiCad/10.0/share/kicad/symbols/Connector_Generic.kicad_sym', 'r') as f:
    text = f.read()
block = re.search(r'\(symbol "Conn_02x10_Odd_Even_1_1".*?\)\n\t\)', text, re.DOTALL)
if block:
    for m in re.finditer(r'\(pin.*?\(at ([\d.-]+) ([\d.-]+) ([\d.-]+)\).*?"(\d+)"', block.group(0), re.DOTALL):
        print(f'Pin {m.group(4)}: {m.group(1)}, {m.group(2)}')
