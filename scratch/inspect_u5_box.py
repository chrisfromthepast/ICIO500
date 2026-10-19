import re

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    c = f.read()

# Let's inspect all tracks in X in [80, 135], Y in [80, 145]
tracks_in_box = []
for m in re.finditer(r'\(segment[\s\S]*?\(start\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(end\s+([\d\.-]+)\s+([\d\.-]+)\)[\s\S]*?\(net\s+"([^"]+)"\)[\s\S]*?\)', c):
    x1, y1 = float(m.group(1)), float(m.group(2))
    x2, y2 = float(m.group(3)), float(m.group(4))
    net = m.group(5)
    if (80 <= x1 <= 135 and 80 <= y1 <= 145) or (80 <= x2 <= 135 and 80 <= y2 <= 145):
        tracks_in_box.append((net, x1, y1, x2, y2, m.group(0)))

vias_in_box = []
for m in re.finditer(r'\(via[\s\S]*?\(at\s+([\d\.-]+)\s+([\d\.-]+)\)[\s\S]*?\(net\s+"([^"]+)"\)[\s\S]*?\)', c):
    x, y = float(m.group(1)), float(m.group(2))
    net = m.group(3)
    if 80 <= x <= 135 and 80 <= y <= 145:
        vias_in_box.append((net, x, y, m.group(0)))

print(f"Tracks in U5 box: {len(tracks_in_box)}")
nets_count = {}
for net, x1, y1, x2, y2, raw in tracks_in_box:
    nets_count[net] = nets_count.get(net, 0) + 1
for net, count in sorted(nets_count.items()):
    print(f"  Track {net:25s}: {count}")

print(f"\nVias in U5 box: {len(vias_in_box)}")
via_nets_count = {}
for net, x, y, raw in vias_in_box:
    via_nets_count[net] = via_nets_count.get(net, 0) + 1
for net, count in sorted(via_nets_count.items()):
    print(f"  Via {net:25s}: {count}")
