import os
import shutil

step_dir = os.path.abspath('build/icio500').replace('\\', '/')
fp_step = f"{step_dir}/faceplate_front.step"

def test_ox(ox_val, label):
    shutil.copy('build/icio500/icio500.kicad_pcb', 'build/icio500/test_ox.kicad_pcb')
    dummy = f'''
\t(footprint "DUMMY_ASSEMBLY"
\t\t(layer "F.Cu")
\t\t(at 52.17 112.15)
\t\t(attr exclude_from_pos_files exclude_from_bom)
\t\t(model "{fp_step}"
\t\t\t(offset (xyz {ox_val} 66.675 -11.11))
\t\t\t(scale (xyz 1 1 1))
\t\t\t(rotate (xyz 0 90 0))
\t\t)
\t)
'''
    with open('build/icio500/test_ox.kicad_pcb', 'r', encoding='utf-8') as f:
        data = f.read()
    idx = data.rfind(')')
    data = data[:idx] + dummy + '\n)'
    with open('build/icio500/test_ox.kicad_pcb', 'w', encoding='utf-8') as f:
        f.write(data)
    
    cmd = f'kicad-cli pcb render --rotate "-35,0,135" --zoom 0.8 -o scratch_3d_{label}.png build/icio500/test_ox.kicad_pcb'
    os.system(cmd)
    print(f"Rendered scratch_3d_{label}.png for ox={ox_val}")

if __name__ == '__main__':
    for ox in [0.0, -10.0, 10.0]:
        test_ox(ox, f"ox_{ox}")
