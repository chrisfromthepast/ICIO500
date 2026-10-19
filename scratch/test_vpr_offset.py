import os
import shutil

step_dir = os.path.abspath('build/icio500').replace('\\', '/')
sat_step = f"{step_dir}/panel_satellite.step"
fp_step = f"{step_dir}/faceplate_front.step"

def make_test(fp_off, sat_off, out_name):
    shutil.copy('build/icio500/icio500.kicad_pcb', 'build/icio500/test_3d.kicad_pcb')
    dummy = f'''
\t(footprint "DUMMY_ASSEMBLY"
\t\t(layer "F.Cu")
\t\t(at 52.17 112.15)
\t\t(attr exclude_from_pos_files exclude_from_bom)
\t\t(model "{fp_step}"
\t\t\t(offset (xyz {fp_off[0]} {fp_off[1]} {fp_off[2]}))
\t\t\t(scale (xyz 1 1 1))
\t\t\t(rotate (xyz 0 90 0))
\t\t)
\t\t(model "{sat_step}"
\t\t\t(offset (xyz {sat_off[0]} {sat_off[1]} {sat_off[2]}))
\t\t\t(scale (xyz 1 1 1))
\t\t\t(rotate (xyz 0 90 0))
\t\t)
\t)
'''
    with open('build/icio500/test_3d.kicad_pcb', 'r', encoding='utf-8') as f:
        data = f.read()
    idx = data.rfind(')')
    data = data[:idx] + dummy + '\n)'
    with open('build/icio500/test_3d.kicad_pcb', 'w', encoding='utf-8') as f:
        f.write(data)
    
    cmd = f'kicad-cli pcb render --rotate "-35,0,135" --zoom 0.8 -o {out_name} build/icio500/test_3d.kicad_pcb'
    os.system(cmd)
    
    cmd3 = f'kicad-cli pcb render --side left --zoom 1.5 -o side_{out_name} build/icio500/test_3d.kicad_pcb'
    os.system(cmd3)

if __name__ == '__main__':
    # oz = 26.99 (or 38.10 - 11.11 = 26.99 mm)
    fp_off = (0.0, 66.675, 26.99)
    # For satellite: ox = -88.0, oy = 266.675, oz = 26.99 + 100 = 126.99
    sat_off = (-88.0, 266.675, 126.99)
    make_test(fp_off, sat_off, 'scratch_vpr_proven_27mm.png')
