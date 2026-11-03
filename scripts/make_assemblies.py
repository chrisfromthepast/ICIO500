import os
import uuid as uuid_mod
import shutil

def gen_assembly():
    fpx = 54.175
    fpy = 102.85  # Exactly centered on carrier card (Y in [45.70, 160.00])
    
    # 2.0 mm Heavy-Duty Active Faceplate (38.10 x 133.35 mm)
    # Faceplate spans Y in [36.175, 169.525] mm (overhangs 9.525 mm top & bottom)
    # Mounted to carrier ears via Wurth WP-SMRA-M3 right-angle brackets
    # Rear face sits directly against carrier ears at X = 54.175 mm
    # Front face at X = 52.175 mm
    # Overall module depth = 203.000 - 52.175 = 150.825 mm = 5.938" (exact VPR-500 standard)
    fp_off = (-2.00, 66.675, -8.74)
    fp_rot = (0, 90, 0)
    
    # Encoder Daughtercard (22.0 x 29.0 mm)
    # Mated to faceplate rear (J2) via 1x5 SMD mezzanine connector (P1)
    # Clamped to faceplate via Bourns PEC11R threaded M7 bushing and nut
    # Standoff: 7.5 mm behind faceplate B.Cu (X = 61.675 mm)
    enc_off = (7.50, -31.675, -8.74)
    enc_rot = (0, 90, 0)
        
    step_dir = os.path.abspath('build/icio500').replace('\\', '/')
    fp_step = f"{step_dir}/faceplate_front.step"
    enc_step = f"{step_dir}/encoder_board.step"
    fp_uuid = str(uuid_mod.uuid4())
    
    pcb_template = f'''
\t(footprint "DUMMY"
\t\t(layer "F.Cu")
\t\t(uuid "{fp_uuid}")
\t\t(at {fpx} {fpy})
\t\t(attr exclude_from_pos_files exclude_from_bom)
\t\t(model "{fp_step}"
\t\t\t(offset (xyz {fp_off[0]} {fp_off[1]} {fp_off[2]}))
\t\t\t(scale (xyz 1 1 1))
\t\t\t(rotate (xyz {fp_rot[0]} {fp_rot[1]} {fp_rot[2]}))
\t\t)
\t\t(model "{enc_step}"
\t\t\t(offset (xyz {enc_off[0]} {enc_off[1]} {enc_off[2]}))
\t\t\t(scale (xyz 1 1 1))
\t\t\t(rotate (xyz {enc_rot[0]} {enc_rot[1]} {enc_rot[2]}))
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
    
    idx = pcb_data.rfind(')')
    pcb_data = pcb_data[:idx] + gen_assembly() + '\n)'
        
    with open(pcb_path, 'w', encoding='utf-8') as f:
        f.write(pcb_data)

if __name__ == "__main__":
    update_assembly_pcb()
    print("Assembly PCB updated successfully!")
