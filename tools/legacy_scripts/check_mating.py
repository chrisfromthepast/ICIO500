import re

print("=" * 60)
print("CONNECTOR MATING ANALYSIS: U6 <-> J1")
print("=" * 60)

# Main board U6
# U6 at PCB (56.0, 103.825), rotated 180
# It's a 2x10 horizontal pin header
# Pad 1 is at the anchor point
# With 180 rotation, pins extend in +Y direction (PCB coords)
# Pin 1 at Y=103.825
# Pin 20 (last row) at Y=103.825 + 9*2.54 = 103.825 + 22.86 = 126.685

# But this is a HORIZONTAL header - the pins stick OUT from the board surface
# The pin plastic body is at X=56.0
# The pins extend LEFT (toward smaller X) because of 180 rotation
# The pin tips would be around X=56.0 - some_length

# In 3D space:
u6_3d_x = 56.0
u6_3d_y_start = -103.825  # Pin 1 Y in 3D
u6_3d_y_end = -(103.825 + 9*2.54)  # Pin 10 Y in 3D
u6_3d_z = 0  # Board surface

print(f"\nU6 (main board) in 3D space:")
print(f"  X = {u6_3d_x} (pad column at PCB X=56)")
print(f"  Y range: {u6_3d_y_end:.3f} to {u6_3d_y_start:.3f}")
print(f"  Z = {u6_3d_z}")

# Satellite J1 at PCB (119.05, 106.35)
# J1 is a 2x10 pin socket (female)
# Satellite board is at PCB X=[100, 138.1], Y=[100, 233.35]
# 
# When the satellite STEP is placed with:
#   offset = (-119.05, 166.675, 0)
#   rotate = (0, -90, 0)
#   DUMMY at PCB (52.17, 112.15) => 3D (52.17, -112.15, 0)
#
# J1's PCB position on satellite: (119.05, 106.35)
# In 3D (before offset/rotation): (119.05, -106.35, 0)
# After offset: (119.05-119.05, -106.35+166.675, 0) = (0, 60.325, 0)
# After Ry=-90:
#   new_x = old_z = 0
#   new_y = old_y = 60.325
#   new_z = -old_x = 0
# After adding DUMMY position: (52.17, -112.15+60.325, 0) = (52.17, -51.825, 0)

j1_3d_x = 52.17
j1_3d_y = -112.15 + 60.325
j1_3d_z = 0

print(f"\nJ1 (satellite) in 3D space:")
print(f"  X = {j1_3d_x}")
print(f"  Y = {j1_3d_y:.3f}")
print(f"  Z = {j1_3d_z}")

print(f"\nMATING CHECK:")
print(f"  U6 Y range: {u6_3d_y_end:.3f} to {u6_3d_y_start:.3f}")
print(f"  J1 Y:       {j1_3d_y:.3f}")
print(f"  J1 should be within U6 Y range: {u6_3d_y_end:.3f} <= {j1_3d_y:.3f} <= {u6_3d_y_start:.3f}")
print(f"  RESULT: {'PASS' if u6_3d_y_end <= j1_3d_y <= u6_3d_y_start else 'FAIL - J1 is OUTSIDE U6 range!'}")

print(f"\n  U6 center Y in 3D:  {(u6_3d_y_start + u6_3d_y_end)/2:.3f}")
print(f"  J1 Y in 3D:         {j1_3d_y:.3f}")
print(f"  Y offset needed:    {(u6_3d_y_start + u6_3d_y_end)/2 - j1_3d_y:.3f}mm")

# J1 is at 3D Y=-51.825 but U6 spans from -126.685 to -103.825
# That's WAY off. J1 is 52mm above U6!
# 
# The problem: satellite Y offset of 166.675 centers the satellite board
# but doesn't align J1 to U6.
# 
# We need J1 at the same Y as U6 center.
# U6 center 3D Y = -(103.825 + 11.43) = -115.255
# 
# J1 satellite PCB Y = 106.35
# J1 3D Y (before offset) = -106.35
# After offset Y: -106.35 + off_y
# After rotation (Y unchanged): -106.35 + off_y
# After DUMMY: -112.15 + (-106.35 + off_y)
# We want: -112.15 + (-106.35 + off_y) = -115.255
# -218.5 + off_y = -115.255
# off_y = 103.245

# But wait - we also need the satellite board height to align properly.
# Satellite board Y range: [100, 233.35]
# After offset off_y=103.245: [-233.35+103.245, -100+103.245] = [-130.105, 3.245]
# After DUMMY: [-112.15+(-130.105), -112.15+3.245] = [-242.255, -108.905]
# That doesn't look right - the satellite would extend way below the main board.

# Let me reconsider. The satellite J1 is near the TOP of the satellite board 
# (Y=106.35 in a board spanning Y=100 to 233.35).
# J1 is only 6.35mm from the top edge.
# The satellite board's TOP edge should align with the left edge of the main board.
# The bottom of the satellite board extends downward.

# In a 500-series module:
# - Main board is horizontal
# - Satellite board is vertical, attached at the left edge
# - The satellite board's connector (J1) mates with the main board's connector (U6)
# - The satellite board hangs DOWN below the main board
# - The faceplate is in front of the satellite, also vertical

# So the satellite's J1 Y position on the satellite PCB tells us how far
# from the satellite's top edge the connector is.
# J1 Y on sat PCB = 106.35, top edge = 100, so J1 is 6.35mm from top.

# In 3D, the satellite should be positioned so that:
# - J1 in 3D Y = U6 pin center in 3D Y
# - The satellite extends downward from there

# U6 center 3D Y = -(103.825 + 11.43) = -115.255
# But actually, what is the U6 center?
# U6 is at PCB Y=103.825, rotated 180, 2x10 header
# The 10 rows span 9*2.54 = 22.86mm
# With 180 rotation, rows extend in +Y direction
# Row 1 at Y=103.825, Row 10 at Y=126.685
# Center Y = (103.825 + 126.685)/2 = 115.255
# In 3D: center Y = -115.255

# J1 on satellite: what are its pin positions?
# J1 is at PCB (119.05, 106.35) - need to know its rotation and type
# It should be a 2x10 socket, matching U6

# Let me check J1 details more carefully

with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    sat = f.read()

# Find J1 footprint block
j1_start = sat.find('"J1"')
if j1_start > 0:
    # Go back to find the footprint start
    fp_start = sat.rfind('(footprint', 0, j1_start)
    # Find the footprint end (matching closing paren)
    block = sat[fp_start:fp_start+500]
    print(f"\nJ1 footprint block (first 500 chars):")
    print(block)
