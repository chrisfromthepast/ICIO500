import os
import shutil

step_dir = os.path.abspath('build/icio500').replace('\\', '/')
fp_step = f"{step_dir}/faceplate_front.step"
sat_step = f"{step_dir}/panel_satellite.step"

def test_both(gap):
    shutil.copy('build/icio500/icio500.kicad_pcb', 'build/icio500/test_both.kicad_pcb')
    # fp_off: ox = 0.0, oy = 66.675, oz = -11.11
    # sat_off: ox = gap, oy = 166.675, oz = -11.11 + 100.0 = 88.89
    dummy = f'''
\t(footprint "DUMMY_ASSEMBLY"
\t\t(layer "F.Cu")
\t\t(at 52.17 112.15)
\t\t(attr exclude_from_pos_files exclude_from_bom)
\t\t(model "{fp_step}"
\t\t\t(offset (xyz 0.0 66.675 -11.11))
\t\t\t(scale (xyz 1 1 1))
\t\t\t(rotate (xyz 0 90 0))
\t\t)
\t\t(model "{sat_step}"
\t\t\t(offset (xyz {gap} 166.675 88.89))
\t\t\t(scale (xyz 1 1 1))
\t\t\t(rotate (xyz 0 90 0))
\t\t)
\t)
'''
    with open('build/icio500/test_both.kicad_pcb', 'r', encoding='utf-8') as f:
        data = f.read()
    idx = data.rfind(')')
    data = data[:idx] + dummy + '\n)'
    with open('build/icio500/test_both.kicad_pcb', 'w', encoding='utf-8') as f:
        f.write(data)
    
    cmd = f'kicad-cli pcb render --rotate "-35,0,135" --zoom 0.8 -o scratch_both_gap{gap}.png build/icio500/test_both.kicad_pcb'
    os.system(cmd)
    print(f"Rendered scratch_both_gap{gap}.png")

if __name__ == '__main__':
    test_both(10.0)
