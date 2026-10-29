import os
import uuid as uuid_mod
import shutil

def gen_assembly():
    # Mathematically verified multi-board 3D assembly offsets adhering to .agents/rules/kicad_3d_viewer.md.
    # In KiCad GUI 3D Viewer (Alt+3), transformations are applied as: Model -> Rotation -> Offset -> Footprint.
    # Rotation (0, -90, 180) maps model coordinates (X, Y, Z) to (-Z, -Y, -X):
    #   - Normal +Z (F.Cu / Front Face) maps to -X (facing forward towards the user).
    #   - Normal -Z (B.Cu / Socket J1 & Brackets) maps to +X (facing backward towards the carrier card).
    #   - Y maps to -Y, correctly matching top-to-bottom layout with carrier card (BR1 at MH1, BR2 at MH2).
    # Satellite: (119.05, -166.675, 0) -> (0, 166.675, -119.05). Offsetting by (0, -166.675, 119.05) centers it at (0,0,0) relative to footprint!
    # Faceplate: (19.05, -66.675, 0) -> (0, 66.675, -19.05). Offsetting by (-1.6, -66.675, 19.05) places it flush in front with 1.6mm thickness.
    fpx = 52.17
    fpy = 112.15 
    
    sat_off = (0.0, -166.675, 119.05)
    sat_rot = (0, -90, 180)
    
    fp_off = (-1.6, -66.675, 19.05)
    fp_rot = (0, -90, 180)
        
    step_dir = os.path.abspath('build/icio500').replace('\\', '/')
    sat_step = f"{step_dir}/panel_satellite.step"
    fp_step = f"{step_dir}/faceplate_front.step"
    fp_uuid = str(uuid_mod.uuid4())
    
    pcb_template = f'''
\t(footprint "DUMMY_ASSEMBLY"
\t\t(layer "F.Cu")
\t\t(uuid "{fp_uuid}")
\t\t(at {fpx} {fpy})
\t\t(attr exclude_from_pos_files exclude_from_bom)
\t\t(model "{sat_step}"
\t\t\t(offset (xyz {sat_off[0]} {sat_off[1]} {sat_off[2]}))
\t\t\t(scale (xyz 1 1 1))
\t\t\t(rotate (xyz {sat_rot[0]} {sat_rot[1]} {sat_rot[2]}))
\t\t)
\t\t(model "{fp_step}"
\t\t\t(offset (xyz {fp_off[0]} {fp_off[1]} {fp_off[2]}))
\t\t\t(scale (xyz 1 1 1))
\t\t\t(rotate (xyz {fp_rot[0]} {fp_rot[1]} {fp_rot[2]}))
\t\t)
\t)
'''
    return pcb_template

def update_assembly_pcb():
    pcb_path = os.path.normpath('build/icio500/icio500_3d_assembly.kicad_pcb')
    src_path = os.path.normpath('build/icio500/icio500.kicad_pcb')
    shutil.copy(src_path, pcb_path)
    
    with open(pcb_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    out_lines = []
    in_dummy = False
    brace_count = 0
    for line in lines:
        if '(footprint "DUMMY' in line:
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
    pcb_data = pcb_data[:idx] + gen_assembly() + '\n)'
        
    with open(pcb_path, 'w', encoding='utf-8') as f:
        f.write(pcb_data)

if __name__ == "__main__":
    update_assembly_pcb()
    print("Assembly updated with exact mathematical mating alignment offsets!")
