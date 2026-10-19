import os
import shutil

step_dir = os.path.abspath('build/icio500').replace('\\', '/')
fp_step = f"{step_dir}/faceplate_front.step"

def test_oz(oz_val, label):
    shutil.copy('build/icio500/icio500.kicad_pcb', 'build/icio500/test_oz.kicad_pcb')
    dummy = f'''
\t(footprint "DUMMY_ASSEMBLY"
\t\t(layer "F.Cu")
\t\t(at 52.17 112.15)
\t\t(attr exclude_from_pos_files exclude_from_bom)
\t\t(model "{fp_step}"
\t\t\t(offset (xyz 0.0 66.675 {oz_val}))
\t\t\t(scale (xyz 1 1 1))
\t\t\t(rotate (xyz 0 90 0))
\t\t)
\t)
'''
    with open('build/icio500/test_oz.kicad_pcb', 'r', encoding='utf-8') as f:
        data = f.read()
    idx = data.rfind(')')
    data = data[:idx] + dummy + '\n)'
    with open('build/icio500/test_oz.kicad_pcb', 'w', encoding='utf-8') as f:
        f.write(data)
    
    cmd = f'kicad-cli pcb render --side left --zoom 1.5 -o scratch_side_{label}.png build/icio500/test_oz.kicad_pcb'
    os.system(cmd)
    print(f"Rendered scratch_side_{label}.png for oz={oz_val}")

if __name__ == '__main__':
    for oz in [0.0, -11.11, 11.11, -26.99, 26.99]:
        test_oz(oz, f"oz_{oz}")
