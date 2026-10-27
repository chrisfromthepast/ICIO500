import os
import uuid as uuid_mod
import shutil
import subprocess

def gen_assembly(cli_mode=False):
    fpx = 55.39
    fpy = 112.15 
    
    sat_off = (-0.08, 166.675, -108.74)
    fp_off = (-1.68, 66.675, -8.74)
        
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

def update_assembly_pcb():
    pcb_path = 'build/icio500/icio500_3d_assembly.kicad_pcb'
    # Always pull latest from main PCB
    shutil.copy('build/icio500/icio500.kicad_pcb', pcb_path)
    
    with open(pcb_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    out_lines = []
    in_dummy = False
    brace_count = 0
    for line in lines:
        if '(footprint "DUMMY"' in line:
            in_dummy = True
            brace_count = 0
            
        if in_dummy:
            brace_count += line.count('(')
            brace_count -= line.count(')')
            if brace_count == 0:
                in_dummy = False
            continue
            
        out_lines.append(line)
        
    pcb_data = "".join(out_lines)
    
    # insert dummy before the last ')'
    idx = pcb_data.rfind(')')
    pcb_data = pcb_data[:idx] + gen_assembly(cli_mode=False) + '\n)'
        
    with open(pcb_path, 'w', encoding='utf-8') as f:
        f.write(pcb_data)

if __name__ == "__main__":
    update_assembly_pcb()
    print("Assemblies forcefully updated with exact original formatting!")
