"""
Fix the pre-existing short between GND via and audio_out_to_1646 diagonal trace.

The GND via at (159.5, 76.5) sits directly in the path of the audio_out_to_1646
diagonal trace from (158.839, 77.291) to (160.275, 75.855).

Fix: Move the GND via ~1.5mm west to (158.0, 76.0) and update the connecting
GND segment from C19 pad (159.5, 78.0) to match the new via position.
"""
import re

PCB_PATH = 'build/icio500/icio500.kicad_pcb'

with open(PCB_PATH, encoding='utf-8') as f:
    pcb = f.read()

# Find all GND segments near the via area
print("=== GND segments near (159.5, 76.5) ===")
for m in re.finditer(
    r'\(segment\s+\(start ([\d.]+) ([\d.]+)\)\s+\(end ([\d.]+) ([\d.]+)\)\s+\(width ([\d.]+)\)\s+\(layer "([^"]+)"\)\s+\(net "gnd"\)',
    pcb
):
    sx, sy = float(m.group(1)), float(m.group(2))
    ex, ey = float(m.group(3)), float(m.group(4))
    layer = m.group(6)
    for x, y in [(sx, sy), (ex, ey)]:
        if abs(x - 159.5) < 3 and abs(y - 76.5) < 3:
            print(f"  ({sx}, {sy}) -> ({ex}, {ey}) on {layer}, width={m.group(5)}")
            break

# 1. Move the GND via from (159.5, 76.5) to (158.0, 76.0)
#    This places it west of the audio diagonal
NEW_VIA_X = 158.0
NEW_VIA_Y = 76.0

old_via = (
    '\t(via\r\n'
    '\t\t(at 159.5 76.5)\r\n'
)
new_via = (
    '\t(via\r\n'
    f'\t\t(at {NEW_VIA_X} {NEW_VIA_Y})\r\n'
)

if old_via in pcb:
    pcb = pcb.replace(old_via, new_via, 1)
    print(f"\nMoved GND via from (159.5, 76.5) to ({NEW_VIA_X}, {NEW_VIA_Y})")
else:
    print("\nERROR: Could not find via to move!")

# 2. Update the GND segment that connects to the via
#    Old: (159.5, 78.0) -> (159.5, 76.5) 
#    New: (159.5, 78.0) -> (158.0, 76.0)  (diagonal to new via position)
old_seg_end = '(start 159.5 78)\r\n\t\t(end 159.5 76.5)'
new_seg_end = f'(start 159.5 78)\r\n\t\t(end {NEW_VIA_X} {NEW_VIA_Y})'

if old_seg_end in pcb:
    pcb = pcb.replace(old_seg_end, new_seg_end, 1)
    print(f"Updated GND segment endpoint to ({NEW_VIA_X}, {NEW_VIA_Y})")
else:
    print("ERROR: Could not find GND segment to update!")

with open(PCB_PATH, 'w', encoding='utf-8') as f:
    f.write(pcb)

print("\nSaved. Run DRC to verify.")
