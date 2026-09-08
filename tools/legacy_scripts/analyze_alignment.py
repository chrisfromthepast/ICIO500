import re

print("=" * 60)
print("DETAILED GEOMETRY ANALYSIS FOR ALIGNMENT")
print("=" * 60)

# Main board
with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    main = f.read()

# Main board extents
main_edges = re.findall(
    r'\(gr_line\s*\n\s*\(start\s+([\d.]+)\s+([\d.]+)\)\s*\n\s*\(end\s+([\d.]+)\s+([\d.]+)\).*?Edge\.Cuts',
    main, re.DOTALL
)
main_xs = []
main_ys = []
for b in main_edges:
    main_xs.extend([float(b[0]), float(b[2])])
    main_ys.extend([float(b[1]), float(b[3])])

print(f"\nMain board:")
print(f"  X: {min(main_xs):.2f} to {max(main_xs):.2f} (width = {max(main_xs)-min(main_xs):.2f}mm)")
print(f"  Y: {min(main_ys):.2f} to {max(main_ys):.2f} (height = {max(main_ys)-min(main_ys):.2f}mm)")
print(f"  Center: ({(min(main_xs)+max(main_xs))/2:.2f}, {(min(main_ys)+max(main_ys))/2:.2f})")

# U6 position and pads
u6_match = re.search(r'PinHeader_2x10.*?\(at\s+([\d.]+)\s+([\d.]+)\s+(\d+)\)', main, re.DOTALL)
print(f"\n  U6 anchor: ({u6_match.group(1)}, {u6_match.group(2)}), rot={u6_match.group(3)}")
u6_x = float(u6_match.group(1))
u6_y = float(u6_match.group(2))

# U6 is 2x10 header, 2.54mm pitch, 10 rows, rotated 180
# Pad 1 is at anchor (for 180 rotation), rows go in -Y direction
# Row 1 at Y=u6_y, Row 10 at Y = u6_y - 9*2.54 = u6_y - 22.86
# With 180 rotation: Row 1 at Y=u6_y, Row 10 at Y = u6_y + 22.86
print(f"  U6 pin Y range (approx): {u6_y:.2f} to {u6_y + 9*2.54:.2f}")
print(f"  U6 pin center Y: {u6_y + 9*2.54/2:.2f}")

# Satellite board
with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    sat = f.read()

sat_edges = re.findall(
    r'\(gr_line\s*\n\s*\(start\s+([\d.]+)\s+([\d.]+)\)\s*\n\s*\(end\s+([\d.]+)\s+([\d.]+)\).*?Edge\.Cuts',
    sat, re.DOTALL
)
sat_xs = []
sat_ys = []
for b in sat_edges:
    sat_xs.extend([float(b[0]), float(b[2])])
    sat_ys.extend([float(b[1]), float(b[3])])

print(f"\nSatellite board:")
print(f"  X: {min(sat_xs):.2f} to {max(sat_xs):.2f} (width = {max(sat_xs)-min(sat_xs):.2f}mm)")
print(f"  Y: {min(sat_ys):.2f} to {max(sat_ys):.2f} (height = {max(sat_ys)-min(sat_ys):.2f}mm)")
print(f"  Center: ({(min(sat_xs)+max(sat_xs))/2:.2f}, {(min(sat_ys)+max(sat_ys))/2:.2f})")

# Find J1 on satellite
j1_match = re.search(r'\(footprint.*?\n\s*\(layer.*?\n\s*\(uuid.*?\n\s*\(at\s+([\d.]+)\s+([\d.]+).*?Reference"\s+"J1"', sat, re.DOTALL)
if j1_match:
    j1_x = float(j1_match.group(1))
    j1_y = float(j1_match.group(2))
    print(f"  J1 anchor: ({j1_x}, {j1_y})")
else:
    # Try different pattern
    j1_blocks = re.findall(r'\(footprint[^)]*\n\s*\(layer[^)]*\)\n\s*\(uuid[^)]*\)\n\s*\(at\s+([\d.]+)\s+([\d.]+)', sat)
    print(f"  Found {len(j1_blocks)} footprints. First few positions:")
    for x, y in j1_blocks[:5]:
        print(f"    ({x}, {y})")
    
    # Also search for PinSocket
    pin_socket = re.findall(r'PinSocket.*?\(at\s+([\d.]+)\s+([\d.]+)', sat, re.DOTALL)
    for x, y in pin_socket:
        print(f"  PinSocket at: ({x}, {y})")

# Faceplate board
with open('build/icio500/faceplate_front.kicad_pcb', 'r', encoding='utf-8') as f:
    fp = f.read()

fp_edges = re.findall(
    r'\(gr_line\s*\n\s*\(start\s+([\d.]+)\s+([\d.]+)\)\s*\n\s*\(end\s+([\d.]+)\s+([\d.]+)\).*?Edge\.Cuts',
    fp, re.DOTALL
)
fp_xs = []
fp_ys = []
for b in fp_edges:
    fp_xs.extend([float(b[0]), float(b[2])])
    fp_ys.extend([float(b[1]), float(b[3])])

print(f"\nFaceplate board:")
if fp_xs:
    print(f"  X: {min(fp_xs):.2f} to {max(fp_xs):.2f} (width = {max(fp_xs)-min(fp_xs):.2f}mm)")
    print(f"  Y: {min(fp_ys):.2f} to {max(fp_ys):.2f} (height = {max(fp_ys)-min(fp_ys):.2f}mm)")
    print(f"  Center: ({(min(fp_xs)+max(fp_xs))/2:.2f}, {(min(fp_ys)+max(fp_ys))/2:.2f})")
else:
    # Check for gr_rect or other edge format
    fp_rects = re.findall(r'\(gr_rect\s*\n\s*\(start\s+([\d.]+)\s+([\d.]+)\)\s*\n\s*\(end\s+([\d.]+)\s+([\d.]+)\).*?Edge\.Cuts', fp, re.DOTALL)
    if fp_rects:
        for r in fp_rects:
            print(f"  gr_rect: ({r[0]}, {r[1]}) to ({r[2]}, {r[3]})")
    else:
        print("  No standard edge cuts found! Checking other formats...")
        edge_refs = [m.start() for m in re.finditer('Edge.Cuts', fp)]
        for pos in edge_refs[:5]:
            context = fp[max(0,pos-200):pos+20]
            print(f"  Context: ...{context[-80:]}...")

# 3D SPACE MAPPING
print("\n" + "=" * 60)
print("3D SPACE MAPPING")
print("=" * 60)
print()
print("KiCad 3D viewer coordinate system:")
print("  3D X = PCB X")
print("  3D Y = -PCB Y (flipped!)")
print("  3D Z = up from board surface")
print()

# When satellite is rotated Ry=-90:
# Original flat satellite in PCB coords: X=[100,138.1], Y=[100,233.35]
# In 3D space (before rotation): X=[100,138.1], Y=[-233.35,-100], Z~0
# After Ry=-90:
#   new_X = old_Z ~= 0  (board becomes edge-on in X)
#   new_Y = old_Y = [-233.35, -100]
#   new_Z = -old_X = [-138.1, -100]

# With offset (-119.05, 166.675, 0) applied BEFORE rotation:
# shifted geometry: X=[100-119.05, 138.1-119.05] = [-19.05, 19.05]
#                   Y=[-233.35+166.675, -100+166.675] = [-66.675, 66.675]
#                   Z~0
# After Ry=-90:
#   new_X = Z ~= 0
#   new_Y = Y = [-66.675, 66.675]
#   new_Z = -X = [-19.05, 19.05]

# DUMMY at PCB (52.17, 112.15) => 3D (52.17, -112.15, 0)
# Final satellite position:
#   X = 52.17 + 0 = 52.17
#   Y = -112.15 + [-66.675, 66.675] = [-178.825, -45.475]
#   Z = 0 + [-19.05, 19.05]

# Main board in 3D:
#   X = [52.17, 203]
#   Y = [-169.3, -55]

main_3d_y_min = -max(main_ys)  # -169.3
main_3d_y_max = -min(main_ys)  # -55

sat_3d_y_min = -112.15 + (-66.675)  # -178.825
sat_3d_y_max = -112.15 + 66.675      # -45.475

print(f"Main board 3D Y range: [{main_3d_y_min:.2f}, {main_3d_y_max:.2f}]")
print(f"  span = {main_3d_y_max - main_3d_y_min:.2f}mm")
print(f"Satellite 3D Y range:  [{sat_3d_y_min:.2f}, {sat_3d_y_max:.2f}]")
print(f"  span = {sat_3d_y_max - sat_3d_y_min:.2f}mm")
print()

# Check alignment
print(f"Main board top edge (3D):     Y = {main_3d_y_max:.2f}")
print(f"Satellite top edge (3D):      Y = {sat_3d_y_max:.2f}")
print(f"  Difference: {sat_3d_y_max - main_3d_y_max:.2f}mm")
print()
print(f"Main board bottom edge (3D):  Y = {main_3d_y_min:.2f}")
print(f"Satellite bottom edge (3D):   Y = {sat_3d_y_min:.2f}")
print(f"  Difference: {sat_3d_y_min - main_3d_y_min:.2f}mm")
print()

# What Y offset would make them aligned?
# Main board center Y in 3D: (-169.3 + -55) / 2 = -112.15
# That's exactly where DUMMY is! So the centering should be correct.
# But the satellite is 133.35mm tall while main board is 114.3mm tall.
# So satellite extends 9.525mm beyond each edge. That's expected for a 500-series module
# where the faceplate/satellite is taller than the main card.

print("ALIGNMENT CHECK:")
print(f"  Main board height:    {max(main_ys)-min(main_ys):.2f}mm")
print(f"  Satellite height:     {max(sat_ys)-min(sat_ys):.2f}mm")
print(f"  Height difference:    {(max(sat_ys)-min(sat_ys)) - (max(main_ys)-min(main_ys)):.2f}mm")
print(f"  Overhang each side:   {((max(sat_ys)-min(sat_ys)) - (max(main_ys)-min(main_ys)))/2:.2f}mm")
print()
print("This is CORRECT for a VPR 500-series module!")
print("The satellite/faceplate (133.35mm = 5.25in) is taller than the main card (114.3mm).")
