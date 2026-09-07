import os
import uuid as uuid_mod
import shutil

def gen_assembly(cli_mode=False):
    fpx = 52.17
    fpy = 112.15 # in PCB (so -112.15 in 3D)
    
    # Using Ry = 90 (to make faceplate face LEFT / user)
    # Geo_X = 119.05
    # Rot_Z (Ry=90) = -Geo_X = -119.05
    # Final_Z = 0 = Rot_Z + Offset_Z => Offset_Z = 119.05
    
    gui_sat_off = (0, 166.675, 119.05)
    gui_fp_off = (0, 66.675, 19.05)
    
    cli_sat_off = (-119.05, 166.675, 0)
    cli_fp_off = (-19.05, 66.675, 0)
    
    if cli_mode:
        sat_off = cli_sat_off
        fp_off = cli_fp_off
    else:
        sat_off = gui_sat_off
        fp_off = gui_fp_off
        
    step_dir = os.path.abspath('build/icio500').replace('\\', '/')
    sat_step = f"{step_dir}/panel_satellite.step"
    fp_step = f"{step_dir}/faceplate_front.step"
    fp_uuid = str(uuid_mod.uuid4())
    
    pcb_template = f'''
\t(footprint "DUMMY"
\t\t(layer "F.Cu")
\t\t(uuid "{fp_uuid}")
\t\t(at {fpx} {fpy})
\t\t(attr exclude_from_pos_files exclude_from_bom)
\t\t(model "{sat_step}"
\t\t\t(offset (xyz {sat_off[0]} {sat_off[1]} {sat_off[2]}))
\t\t\t(scale (xyz 1 1 1))
\t\t\t(rotate (xyz 0 90 0))
\t\t)
\t\t(model "{fp_step}"
\t\t\t(offset (xyz {fp_off[0]} {fp_off[1]} {fp_off[2]}))
\t\t\t(scale (xyz 1 1 1))
\t\t\t(rotate (xyz 0 90 0))
\t\t)
\t)
'''
    return pcb_template

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

shutil.copy('build/icio500/icio500.kicad_pcb', 'build/icio500/icio500_3d_assembly.kicad_pcb')
with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'w', encoding='utf-8') as f:
    insert_pos = pcb.rfind(')')
    f.write(pcb[:insert_pos] + gen_assembly(cli_mode=False) + ')')
print("Written GUI assembly with Ry=90!")
