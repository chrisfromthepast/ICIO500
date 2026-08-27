"""Find all segments and vias of the audio_out_to_1646 and nearby GND items."""
import re

pcb = open('build/icio500/icio500.kicad_pcb', encoding='utf-8').read()

print("=== audio_out_to_1646 segments ===")
for m in re.finditer(
    r'\(segment\s+\(start ([\d.]+) ([\d.]+)\)\s+\(end ([\d.]+) ([\d.]+)\)\s+\(width ([\d.]+)\)\s+\(layer "([^"]+)"\)\s+\(net "audio_out_to_1646"\)',
    pcb
):
    print(f"  ({m.group(1)},{m.group(2)}) -> ({m.group(3)},{m.group(4)}) w={m.group(5)} layer={m.group(6)}")

print()
print("=== GND vias ===")
for m in re.finditer(
    r'\(via\s+\(at ([\d.]+) ([\d.]+)\)\s+\(size ([\d.]+)\).*?\(net "gnd"\)',
    pcb, re.DOTALL
):
    x, y = float(m.group(1)), float(m.group(2))
    if 155 < x < 165 and 74 < y < 82:
        print(f"  via at ({x}, {y}) size={m.group(3)}")

print()
print("=== GND segments near audio area (155<x<165, 74<y<82) ===")
for m in re.finditer(
    r'\(segment\s+\(start ([\d.]+) ([\d.]+)\)\s+\(end ([\d.]+) ([\d.]+)\)\s+\(width ([\d.]+)\)\s+\(layer "([^"]+)"\)\s+\(net "gnd"\)',
    pcb
):
    sx, sy = float(m.group(1)), float(m.group(2))
    ex, ey = float(m.group(3)), float(m.group(4))
    for x, y in [(sx,sy),(ex,ey)]:
        if 153 < x < 165 and 74 < y < 82:
            print(f"  ({sx},{sy}) -> ({ex},{ey}) layer={m.group(6)}")
            break
