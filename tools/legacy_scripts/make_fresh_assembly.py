import re
import uuid as uuid_mod
import shutil
import os

print("=" * 60)
print("RECALCULATING 3D OFFSETS FOR PROPER J1-U6 MATING")
print("=" * 60)

# KEY FACTS:
# Main board U6: PCB (56.0, 103.825), rot=180
#   2x10 horizontal header, pins extend LEFT
#   Pin rows at Y = 103.825 to 103.825+22.86 = 126.685 (due to 180 rot)
#   U6 center Y on PCB = 115.255
#   U6 center Y in 3D = -115.255

# Satellite J1: PCB (119.05, 175.0), rot=0
#   2x10 SMD pin socket
#   Pin rows at Y = 175.0 - 11.43 to 175.0 + 11.43 = 163.57 to 186.43
#   J1 center Y on PCB = 175.0
#   J1 center Y in STEP 3D = -175.0

# Satellite board: PCB X=[100,138.1], Y=[100,233.35]
#   Center: (119.05, 166.675)
#   In STEP 3D: X=[100,138.1], Y=[-233.35,-100]

# We need J1 3D Y to equal U6 3D Y center:
#   J1 final 3D Y = DUMMY_3D_Y + (sat_J1_3D_Y + offset_Y)  [Y unchanged by Ry rotation]
#   -115.255 = -112.15 + (-175.0 + offset_Y)
#   -115.255 = -112.15 - 175.0 + offset_Y
#   -115.255 = -287.15 + offset_Y
#   offset_Y = -115.255 + 287.15 = 171.895

# For X alignment (becomes Z after Ry=-90 rotation):
#   After rotation, old_X maps to -new_Z
#   We want the satellite to be AT the main board's left edge
#   offset_X = -119.05 (centers X at 0, so Z=0 after rotation, which aligns with DUMMY X=52.17)
# Actually wait, let me reconsider. After offset, the geometry X becomes:
#   100-119.05 to 138.1-119.05 = -19.05 to 19.05
# After Ry=-90: new_Z = -old_X = -(-19.05) to -(19.05) = 19.05 to -19.05
# Final Z = 0 + (19.05 to -19.05) = extends equally above and below
# Final X = DUMMY_X + old_Z = 52.17 + 0 = 52.17
# The satellite board is at X=52.17, which IS the left edge of the main board. Good.

sat_off_x = -119.05
sat_off_y = 171.895  # CRITICAL FIX: was 166.675, now 171.895 to align J1 with U6
sat_off_z = 0

print(f"\nSatellite offset: ({sat_off_x}, {sat_off_y}, {sat_off_z})")

# Verify J1 alignment:
j1_final_y = -112.15 + (-175.0 + sat_off_y)
print(f"J1 final 3D Y: {j1_final_y:.3f}")
print(f"U6 center 3D Y: -115.255")
print(f"Difference: {j1_final_y - (-115.255):.3f}mm")

# Verify satellite board vertical position:
sat_top_y = -112.15 + (-100.0 + sat_off_y)
sat_bot_y = -112.15 + (-233.35 + sat_off_y)
main_top_y = -55.0
main_bot_y = -169.3
print(f"\nSatellite 3D Y: [{sat_bot_y:.2f}, {sat_top_y:.2f}]")
print(f"Main board 3D Y: [{main_bot_y:.2f}, {main_top_y:.2f}]")
print(f"Satellite top overhang: {sat_top_y - main_top_y:.2f}mm")
print(f"Satellite bottom overhang: {main_bot_y - sat_bot_y:.2f}mm")

# For the faceplate:
# Faceplate board: PCB X=[0,38.1], Y=[0,133.35], center=(19.05, 66.675)
# The faceplate should align vertically with the satellite board.
# Satellite 3D Y range: [sat_bot_y, sat_top_y]
# Faceplate 3D Y (before offset): Y=[-133.35, 0], center=-66.675
# After offset Y: [-133.35+off_y, 0+off_y]
# After DUMMY: [-112.15 + (-133.35+off_y), -112.15 + (0+off_y)]
# We want this to equal [sat_bot_y, sat_top_y]:
#   -112.15 + (-133.35+off_y) = sat_bot_y
#   off_y = sat_bot_y + 112.15 + 133.35
#   off_y = -173.60 + 112.15 + 133.35 = 71.9

fp_off_y = sat_bot_y + 112.15 + 133.35
fp_off_x = -19.05  # Centers X at 0
fp_off_z = 0

# Verify faceplate alignment:
fp_top_y = -112.15 + (0 + fp_off_y)
fp_bot_y = -112.15 + (-133.35 + fp_off_y)
print(f"\nFaceplate offset: ({fp_off_x}, {fp_off_y:.3f}, {fp_off_z})")
print(f"Faceplate 3D Y: [{fp_bot_y:.2f}, {fp_top_y:.2f}]")
print(f"Satellite 3D Y: [{sat_bot_y:.2f}, {sat_top_y:.2f}]")
print(f"Top alignment: {fp_top_y - sat_top_y:.3f}mm (should be 0)")
print(f"Bot alignment: {fp_bot_y - sat_bot_y:.3f}mm (should be 0)")

print(f"\n{'='*60}")
print("FINAL OFFSETS:")
print(f"{'='*60}")
print(f"DUMMY at PCB (52.17, 112.15)")
print(f"Satellite: offset=({sat_off_x}, {sat_off_y}, {sat_off_z}), rotate=(0, -90, 0)")
print(f"Faceplate: offset=({fp_off_x}, {fp_off_y:.3f}, {fp_off_z}), rotate=(0, -90, 0)")

# Now generate the assembly file
print(f"\nGenerating assembly file...")

shutil.copy('build/icio500/icio500.kicad_pcb', 'build/icio500/icio500_3d_assembly.kicad_pcb')

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

step_dir = os.path.abspath('build/icio500').replace('\\', '/')
sat_step = f"{step_dir}/panel_satellite.step"
fp_step = f"{step_dir}/faceplate_front.step"

fp_uuid = str(uuid_mod.uuid4())

dummy = f'''
\t(footprint "DUMMY"
\t\t(layer "F.Cu")
\t\t(uuid "{fp_uuid}")
\t\t(at 52.17 112.15)
\t\t(attr exclude_from_pos_files exclude_from_bom)
\t\t(model "{sat_step}"
\t\t\t(offset
\t\t\t\t(xyz {sat_off_x} {sat_off_y} {sat_off_z})
\t\t\t)
\t\t\t(scale
\t\t\t\t(xyz 1 1 1)
\t\t\t)
\t\t\t(rotate
\t\t\t\t(xyz 0 -90 0)
\t\t\t)
\t\t)
\t\t(model "{fp_step}"
\t\t\t(offset
\t\t\t\t(xyz {fp_off_x} {fp_off_y:.3f} {fp_off_z})
\t\t\t)
\t\t\t(scale
\t\t\t\t(xyz 1 1 1)
\t\t\t)
\t\t\t(rotate
\t\t\t\t(xyz 0 -90 0)
\t\t\t)
\t\t)
\t)
'''

insert_pos = pcb.rfind('\n)')
pcb = pcb[:insert_pos] + dummy + pcb[insert_pos:]

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)

print("Assembly file generated!")
