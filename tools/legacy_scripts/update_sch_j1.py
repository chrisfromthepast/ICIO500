import re
import uuid

with open('build/icio500/faceplate_logic.kicad_sch', 'r', encoding='utf-8') as f:
    sch = f.read()

# Find J1 block
j1_match = re.search(r'\(symbol\s+\(lib_id "Connector_Generic:Conn_01x08".*?\(property "Reference" "J1".*?\n  \)', sch, re.DOTALL)
if not j1_match:
    print("Could not find J1!")
    exit(1)

j1_start = j1_match.start()
j1_end = j1_match.end()

new_j1 = """(symbol (lib_id "Connector_Generic:Conn_02x10_Odd_Even") (at 30 50 0) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uuid1}")
    (property "Reference" "J1" (at 30 35 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "Conn_02x10" (at 30 37 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
  )""".format(uuid1=str(uuid.uuid4()))

sch = sch[:j1_start] + new_j1 + sch[j1_end:]

# Add labels
pins = {
    1: (-5.08, 10.16), 2: (7.62, 10.16),
    3: (-5.08, 7.62), 4: (7.62, 7.62),
    5: (-5.08, 5.08), 6: (7.62, 5.08),
    7: (-5.08, 2.54), 8: (7.62, 2.54),
    9: (-5.08, 0), 10: (7.62, 0)
}

nets = {
    1: '+3V3', 2: '+3V3',
    3: 'GND', 4: 'SDA',
    5: 'GND', 6: 'SCL',
    7: 'GND', 8: 'ENC_A',
    9: 'ENC_B', 10: 'ENC_SW'
}

labels = ""
for pin, net in nets.items():
    px, py = pins[pin]
    # Absolute coordinates
    ax = 30 + px
    ay = 50 - py
    rot = 0 if px < 0 else 180
    labels += f'\n  (global_label "{net}" (shape input) (at {ax} {ay} {rot}) (fields_autoplaced yes) (uuid "{str(uuid.uuid4())}") (property "Intersheet References" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes))))'

# Insert labels right before the closing paren of the schematic
end_pos = sch.rfind(')')
sch = sch[:end_pos] + labels + "\n" + sch[end_pos:]

with open('build/icio500/faceplate_logic.kicad_sch', 'w', encoding='utf-8') as f:
    f.write(sch)

print("Updated J1 and wired nets in schematic!")
