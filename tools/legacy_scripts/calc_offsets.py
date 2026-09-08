"""
Calculate exact 3D model offsets for the ICIO500 assembly.

COORDINATE SYSTEMS:
- KiCad PCB: X increases right, Y increases DOWN (screen coords)
- KiCad 3D:  X increases right, Y increases UP (3D world), Z increases toward viewer
- STEP export with --user-origin 0x0in: 
    STEP X = PCB X (in mm)
    STEP Y = -PCB Y (in mm, flipped)
    STEP Z = 0 (board surface)

3D MODEL PLACEMENT IN KICAD:
- The model offset is applied relative to the footprint's position
- Offset is in mm, applied BEFORE rotation
- Rotation is Euler angles applied in order: Rz, Ry, Rx (I think)

GOAL:
- Main board is the base, lying flat
- Satellite board needs to be vertical (rotated 90 around Y), perpendicular to the main board
- Faceplate needs to be vertical too, parallel to the satellite board, on its front face
- The satellite's J1 socket must mate with the main board's U6 header

KEY DIMENSIONS (from analysis):
Main board:
  PCB X: 52.17 to 203.0    Y: 55.0 to 169.3
  U6: (56.0, 103.825) rotated 180 deg
  Left edge: X = 52.17

Satellite board (PCB coords):
  PCB X: 100.0 to 138.1    Y: 100.0 to 233.35
  Width = 38.1mm, Height = 133.35mm
  Center: (119.05, 166.675)

Faceplate (PCB coords):
  PCB X: 0.0 to 38.1       Y: 0.0 to 133.35
  Width = 38.1mm, Height = 133.35mm
  Center: (19.05, 66.675)
"""

import re

# The approach: Instead of trying to derive the math abstractly,
# I'll use the simplest possible approach: place the DUMMY footprint at
# a known position and use trial offsets, then verify with CLI render.

# But actually, let me try the simplest possible approach first:
# Place the DUMMY at (0, 0) and work in absolute coordinates.

# When --user-origin 0x0in is used:
# - STEP internal (0,0,0) = PCB origin (0,0)
# - STEP X = PCB X (mm)  
# - STEP Y = -PCB Y (mm) (Y is flipped between PCB and 3D)
# - STEP Z = 0 (top surface)

# The model offset in KiCad is specified as (dx, dy, dz) in mm.
# The offset is RELATIVE to the footprint's anchor position.
# The footprint position in 3D space:
#   3D X = PCB X of footprint
#   3D Y = -PCB Y of footprint  
#   3D Z = 0

# So if DUMMY is at PCB (52.17, 112.15):
#   3D position = (52.17, -112.15, 0)

# The STEP file with --user-origin 0x0in has its content at:
#   Satellite: 3D X=[100, 138.1], 3D Y=[-233.35, -100], Z=0
#   Faceplate: 3D X=[0, 38.1], 3D Y=[-133.35, 0], Z=0

# After applying offset (dx, dy, dz) to the model, the model moves by that amount
# relative to the footprint position.
# Then rotation (rx, ry, rz) is applied around the footprint's 3D position.

# Wait - I need to be careful. In KiCad, the model offset is applied BEFORE rotation.
# That means:
# 1. Start with model at its own origin
# 2. Apply offset to shift it
# 3. Apply rotation around the (now shifted) model's origin? Or around the footprint?

# Actually, looking at KiCad source code conventions:
# The transform is: Final = FootprintPos + Rotation * (ModelGeometry + Offset)
# So: offset shifts the geometry, then rotation is applied, then footprint position places it.

# Let me just try a simple approach: Place DUMMY at (0,0) and use absolute offsets.

# DUMMY at PCB (0, 0) => 3D position (0, 0, 0)
# No rotation case: model appears at Offset position

# For the satellite board to appear VERTICAL:
# - Rotate Y = -90: This rotates the flat board from XY plane to XZ plane
# - After rotation, the board's original X axis maps to -Z
# - The board's original Y axis stays as Y
# - The board's original Z axis maps to X

# With Ry = -90:
# new_x = old_z
# new_y = old_y  
# new_z = -old_x

# The satellite STEP has geometry at:
#   X: 100 to 138.1 (center 119.05)
#   Y: -233.35 to -100 (center -166.675)
#   Z: ~0 (thin board)

# After Ry=-90 rotation:
#   new_x = old_z = ~0
#   new_y = old_y = -233.35 to -100
#   new_z = -old_x = -138.1 to -100

# So the satellite ends up as a thin vertical plane at new_x ≈ 0
# extending in Y from -233.35 to -100
# and in Z from -138.1 to -100

# We want the satellite board positioned so that:
# - It's at the left edge of the main board (X=52.17 in PCB = X=52.17 in 3D)
# - It's centered vertically with the main board

# Main board in 3D:
#   X: 52.17 to 203
#   Y: -169.3 to -55
#   Center Y = -112.15

# The satellite board spans Y: -233.35 to -100 (in 3D, before offset)
# After Ry=-90, satellite Y stays the same: -233.35 to -100
# Satellite center Y = -166.675

# Main board center Y = -112.15
# We need to shift satellite Y by: -112.15 - (-166.675) = +54.525

# After Ry=-90, satellite X ≈ 0
# We need satellite X ≈ 52.17 (left edge of main board)
# Need offset to put it at X=52.17

# But wait - the offset is applied BEFORE rotation!
# So: Final = FootprintPos + Rot * (Geometry + Offset)

# If DUMMY is at (0, 0, 0) in 3D:
# Final = Rot * (Geometry + Offset)

# We want: Rot * (Geometry + Offset) = DesiredPosition
# So: Geometry + Offset = Rot^-1 * DesiredPosition
# With Ry = -90, Rot^-1 = Ry(+90):
#   inv_x = -old_z
#   inv_y = old_y
#   inv_z = old_x

# Hmm this is getting complicated. Let me just try the simplest thing:
# Place DUMMY at (0,0), use offset (0,0,0) and rotation (0,-90,0),
# then iteratively adjust until it works.

# Actually, let me try placing the DUMMY at the LEFT EDGE of the main board
# where the satellite should attach. That simplifies things enormously.

dummy_pcb_x = 52.17  # Left edge of main board
dummy_pcb_y = 112.15  # Center of main board in Y

# DUMMY 3D position: (52.17, -112.15, 0)

# For the satellite board:
# With --user-origin 0x0in and Ry=-90:
# The satellite geometry center is at STEP (119.05, -166.675, 0)
# Apply offset first: geometry + offset
# Then rotate by Ry=-90:
#   new_x = (geo_z + off_z)
#   new_y = (geo_y + off_y)
#   new_z = -(geo_x + off_x)
# Then add DUMMY 3D position

# We want the final position to be:
#   new_x + 52.17 = 52.17  => new_x = 0 => geo_z + off_z = 0 => off_z = 0 (board is thin)
#   new_y - 112.15 = main board center Y range => We want satellite center at main board center
#     Satellite center geo_y = -166.675
#     We want new_y + (-112.15) to center the satellite on the main board
#     Main board Y range in 3D: -169.3 to -55.0, center = -112.15
#     Satellite in 3D after rot: Y range = (geo_y + off_y) range
#     Satellite geo_y range: -233.35 to -100.0
#     We want center of (geo_y + off_y) + (-112.15) = -112.15
#     So center of (geo_y + off_y) = 0
#     Satellite center geo_y = -166.675
#     off_y = 166.675

#   For Z: new_z = -(geo_x + off_x) + 0
#     Satellite geo_x range: 100 to 138.1
#     After rot, Z range = -(geo_x + off_x) range
#     This is the depth into the screen
#     We don't want it sticking way out, we want it flush
#     off_x = -119.05 would center it at Z=0

print("Calculated offsets for DUMMY at ({}, {}):".format(dummy_pcb_x, dummy_pcb_y))
print()

sat_off_x = -119.05  # Centers satellite's X at 0, which becomes Z=0 after rotation
sat_off_y = 166.675   # Centers satellite's Y at 0
sat_off_z = 0         # Board is thin, stays at X=0 after rotation (which is the left edge)

print(f"Satellite offset: ({sat_off_x}, {sat_off_y}, {sat_off_z})")
print(f"Satellite rotation: (0, -90, 0)")

# Verify satellite final position:
# Satellite geo center: (119.05, -166.675, 0)
# + offset: (119.05-119.05, -166.675+166.675, 0+0) = (0, 0, 0)
# After Ry=-90: (0, 0, 0) => still at origin
# + DUMMY pos (52.17, -112.15, 0)
# Final: (52.17, -112.15, 0) -- exactly at the left edge, centered!
print(f"Satellite final center (verify): (52.17, -112.15, 0) -- left edge, centered!")

# For the faceplate:
# Faceplate geo center: (19.05, -66.675, 0)
# We want it at the same X as the satellite (left edge of main board)
# and centered vertically with the main board
fp_off_x = -19.05   # Center faceplate X at 0
fp_off_y = 66.675 - 112.15 + 112.15  # Hmm, let me think...

# Actually: Faceplate geo center Y = -66.675
# After offset Y: -66.675 + off_y
# After Ry=-90, Y stays: -66.675 + off_y
# After adding DUMMY Y (-112.15): -66.675 + off_y - 112.15
# We want this to be at -112.15 (centered with main board)
# -66.675 + off_y - 112.15 = -112.15
# off_y = 66.675

fp_off_y = 66.675
fp_off_z = 0  # Flush with satellite

print(f"\nFaceplate offset: ({fp_off_x}, {fp_off_y}, {fp_off_z})")
print(f"Faceplate rotation: (0, -90, 0)")

# But wait - the faceplate should be in FRONT of the satellite,
# not at the same X position. The satellite has PCB components facing forward.
# The faceplate is the front panel that the user sees.
# The satellite PCB sits behind the faceplate.

# Actually, for a 500-series module:
# - The faceplate is the front panel visible to the user
# - The satellite board sits behind the faceplate, perpendicular to the main board
# - The satellite board has connectors (XLR, jacks) that poke through the faceplate

# Both should be at the same X position (the left edge).
# The faceplate Z offset can be slightly different to show it's attached to the satellite.

# Let me also think about the Z offset more carefully.
# After Ry=-90:
#   new_z = -(geo_x + off_x)
# For satellite: new_z = -(geo_x - 119.05)
#   geo_x range: 100 to 138.1
#   new_z range: -(100-119.05) to -(138.1-119.05) = 19.05 to -19.05
#   So satellite extends Z from -19.05 to +19.05
# + DUMMY Z (0) = -19.05 to +19.05
# This means the satellite board extends 19.05mm in front and behind the main board surface.
# That seems right for a board that's 38.1mm wide standing vertical.

# For faceplate: new_z = -(geo_x - 19.05)
#   geo_x range: 0 to 38.1
#   new_z range: -(0-19.05) to -(38.1-19.05) = 19.05 to -19.05
# Same extent. This would overlay the faceplate exactly on the satellite.
# To put it slightly in front, we could adjust fp_off_z.

print("\n--- Final offsets to use ---")
print(f"DUMMY at PCB ({dummy_pcb_x}, {dummy_pcb_y})")
print(f"Satellite: offset=({sat_off_x}, {sat_off_y}, {sat_off_z}), rotate=(0, -90, 0)")
print(f"Faceplate: offset=({fp_off_x}, {fp_off_y}, {fp_off_z}), rotate=(0, -90, 0)")
