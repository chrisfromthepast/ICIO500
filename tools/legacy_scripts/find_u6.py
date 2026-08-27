import re
with open('build/icio500/icio500.kicad_sch', 'r', encoding='utf-8') as f:
    content = f.read()

u6_block = None
for m in re.finditer(r'\(symbol \(lib_id "Connector_Generic:Conn_02x10_Odd_Even".*?\(property "Reference" "U6"', content, re.DOTALL):
    start = m.start()
    depth = 0
    end = start
    for i in range(start, len(content)):
        if content[i] == '(': depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                end = i
                break
    u6_block = content[start:end+1]
    break

if u6_block:
    print("Found U6 in main schematic!")
else:
    print("Could not find U6 in schematic!")
