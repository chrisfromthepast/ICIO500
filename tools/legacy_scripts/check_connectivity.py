import re, math

pcb = open('build/icio500/icio500.kicad_pcb', encoding='utf-8').read()

# Find all footprints and their positions
# Strategy: split by footprint boundaries, extract position and pads

# Find footprint blocks by their start positions
fp_starts = [m.start() for m in re.finditer(r'\n\t\(footprint ', pcb)]
fp_starts.append(len(pcb))

pad_abs_positions = {}  # net_name -> [(abs_x, abs_y), ...]

for i in range(len(fp_starts) - 1):
    fp_text = pcb[fp_starts[i]:fp_starts[i+1]]
    
    # Get footprint position
    at_match = re.search(r'\n\t\t\(at ([\d.e-]+) ([\d.e-]+)(?: ([\d.e-]+))?\)', fp_text)
    if not at_match:
        continue
    fp_x = float(at_match.group(1))
    fp_y = float(at_match.group(2))
    fp_rot = float(at_match.group(3)) if at_match.group(3) else 0.0
    
    # Get reference
    ref_match = re.search(r'"Reference" "([^"]+)"', fp_text)
    ref = ref_match.group(1) if ref_match else '??'
    
    rot_rad = math.radians(-fp_rot)  # KiCad uses CW positive
    
    # Find all pads with nets
    pad_iter = re.finditer(
        r'\(pad "(\d+)"[^\n]*\n\t\t\t\(at ([\d.e-]+) ([\d.e-]+)(?: ([\d.e-]+))?\).*?(?:\(net "([^"]+)"\))',
        fp_text, re.DOTALL
    )
    
    for pm in pad_iter:
        pad_num = pm.group(1)
        pad_x = float(pm.group(2))
        pad_y = float(pm.group(3))
        pad_rot_local = float(pm.group(4)) if pm.group(4) else 0.0
        net_name = pm.group(5)
        
        # Rotate pad offset by footprint rotation
        cos_r = math.cos(rot_rad)
        sin_r = math.sin(rot_rad)
        abs_x = fp_x + pad_x * cos_r - pad_y * sin_r
        abs_y = fp_y + pad_x * sin_r + pad_y * cos_r
        
        if net_name not in pad_abs_positions:
            pad_abs_positions[net_name] = []
        pad_abs_positions[net_name].append((round(abs_x, 4), round(abs_y, 4), ref, pad_num))

# Parse all segments
seg_data = {}  # net -> [(sx, sy, ex, ey), ...]
seg_endpoints_set = {}  # net -> set of rounded endpoints

for m in re.finditer(
    r'\(segment\s+\(start ([\d.e-]+) ([\d.e-]+)\)\s+\(end ([\d.e-]+) ([\d.e-]+)\)\s+\(width ([\d.e-]+)\)\s+\(layer "([^"]+)"\)\s+\(net "([^"]+)"\)',
    pcb
):
    sx, sy, ex, ey = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
    net = m.group(7)
    if net not in seg_data:
        seg_data[net] = []
        seg_endpoints_set[net] = set()
    seg_data[net].append((sx, sy, ex, ey))
    seg_endpoints_set[net].add((round(sx, 2), round(sy, 2)))
    seg_endpoints_set[net].add((round(ex, 2), round(ey, 2)))

# Check connectivity
TOLERANCE = 0.6  # mm

print("=" * 60)
print("NET CONNECTIVITY ANALYSIS")
print("=" * 60)

all_ok = True
for net_name in sorted(pad_abs_positions.keys()):
    pads = pad_abs_positions[net_name]
    endpoints = seg_endpoints_set.get(net_name, set())
    
    connected = []
    disconnected = []
    
    for px, py, ref, pad_num in pads:
        found = False
        for ex, ey in endpoints:
            if abs(px - ex) < TOLERANCE and abs(py - ey) < TOLERANCE:
                found = True
                break
        if found:
            connected.append((px, py, ref, pad_num))
        else:
            disconnected.append((px, py, ref, pad_num))
    
    n_segs = len(seg_data.get(net_name, []))
    
    if disconnected:
        all_ok = False
        print(f"\n[INCOMPLETE] {net_name}: {len(connected)}/{len(pads)} pads connected, {n_segs} segments")
        for px, py, ref, pn in disconnected:
            print(f"   DISCONNECTED: {ref} pad {pn} at ({px:.2f}, {py:.2f})")
        for px, py, ref, pn in connected:
            print(f"   connected:    {ref} pad {pn} at ({px:.2f}, {py:.2f})")
    elif n_segs == 0 and len(pads) > 1:
        all_ok = False
        print(f"\n[NO TRACES] {net_name}: {len(pads)} pads, 0 segments")
        for px, py, ref, pn in pads:
            print(f"   pad: {ref} pad {pn} at ({px:.2f}, {py:.2f})")

if all_ok:
    print("\nAll nets appear fully connected!")
else:
    print(f"\n{'=' * 60}")
    print("Some nets need routing (see above)")
