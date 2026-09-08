import shutil
import uuid as uuid_mod
import os

print("=" * 60)
print("GENERATING ASSEMBLY FOR GUI (Offset AFTER Rotation)")
print("=" * 60)

# The KiCad GUI 3D Viewer applies Offset AFTER Rotation.
# Final = FootprintPos + Rotation * Geometry + Offset
# 
# Satellite Geo J1: (119.05, -175.0, 0)
# Rotated Geo J1 (Ry=-90): (0, -175.0, -119.05)
# FootprintPos: (52.17, -112.15, 0)
# We want Final J1: (52.17, -115.255, 0)  [Aligned with U6 center]
# offset = Final - FootprintPos - RotatedGeo
# off_x = 52.17 - 52.17 - 0 = 0
# off_y = -115.255 - (-112.15) - (-175.0) = 171.895
# off_z = 0 - 0 - (-119.05) = 119.05
sat_off_x = 0
sat_off_y = 171.895
sat_off_z = 119.05

# Faceplate Geo Center: (19.05, -66.675, 0)
# Rotated Geo Center (Ry=-90): (0, -66.675, -19.05)
# FootprintPos: (52.17, -112.15, 0)
# We want Final Center Y aligned with Satellite Center Y (-106.93)
# We want Final Z = 0
# off_x = 52.17 - 52.17 - 0 = 0
# off_y = -106.93 - (-112.15) - (-66.675) = 71.895
# off_z = 0 - 0 - (-19.05) = 19.05
fp_off_x = 0
fp_off_y = 71.895
fp_off_z = 19.05

# For Faceplate, we actually want it slightly in front of the satellite board.
# Satellite spans Z from -19.05 to +19.05
# Front of satellite is Z = 19.05 (in 3D space)
# Faceplate spans Z from -19.05 to +19.05 (relative to its own center)
# So if Faceplate Z center is 0, its front is at 19.05, same as satellite.
# Let's keep it at 0 to be perfectly flush, which is mechanically correct for the PCB stacking.

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
\t\t\t\t(xyz {fp_off_x} {fp_off_y} {fp_off_z})
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

print("Assembly file generated for GUI (Offset AFTER Rotation)!")
print(f"Satellite: offset=({sat_off_x}, {sat_off_y}, {sat_off_z}), rotate=(0, -90, 0)")
print(f"Faceplate: offset=({fp_off_x}, {fp_off_y}, {fp_off_z}), rotate=(0, -90, 0)")
