import subprocess
import os
import shutil
from PIL import Image

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
ASSY_PCB = r"build\icio500\icio500_3d_assembly.kicad_pcb"
FP_PCB = r"build\icio500\faceplate_front.kicad_pcb"
ENC_PCB = r"build\icio500\encoder_board.kicad_pcb"
ART_DIR = r"C:\Users\Chris Williams\.gemini\antigravity\brain\27d96d43-0ba0-4cfa-ba0b-2ac48d075611"
os.makedirs("views", exist_ok=True)

renders = [
    (ASSY_PCB, "views/v18_iso_hero.png", '--rotate "-30,0,135" --zoom 0.85'),
    (ASSY_PCB, "views/v18_iso_brackets.png", '--rotate "-30,0,-45" --zoom 0.85'),
    (ASSY_PCB, "views/v18_top_full.png", '--side top --zoom 0.9'),
    (FP_PCB, "views/v18_faceplate_front.png", '--side top --zoom 0.95'),
    (FP_PCB, "views/v18_faceplate_rear.png", '--side bottom --zoom 0.95'),
    (ENC_PCB, "views/v18_encoder_hero.png", '--rotate "-30,0,135" --zoom 0.9'),
    (ASSY_PCB, "views/v18_bottom_top_check.png", '--side top --zoom 4.0 --pivot "-8.5,-4.8,0"'),
    (ASSY_PCB, "views/v18_bottom_underside_check.png", '--side bottom --zoom 4.0 --pivot "-8.5,-4.8,0"'),
    (ASSY_PCB, "views/v18_bracket2_screw_clearance.png", '--rotate "-35,0,-45" --zoom 2.8 --pivot "-5.5,-4.5,0"'),
]

for pcb, out, flags in renders:
    cmd = f'"{KICAD_CLI}" pcb render {flags} -o "{out}" "{pcb}"'
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)
    print(f"Rendered: {out}")

crop_list = [
    'v18_iso_hero', 'v18_iso_brackets', 'v18_top_full', 'v18_faceplate_front',
    'v18_faceplate_rear', 'v18_encoder_hero', 'v18_bottom_top_check',
    'v18_bottom_underside_check', 'v18_bracket2_screw_clearance'
]
for base in crop_list:
    src = f"views/{base}.png"
    if os.path.exists(src):
        im = Image.open(src)
        bbox = im.getbbox()
        if bbox:
            cropped = im.crop(bbox)
            crop_path = f"views/{base}_crop.png"
            cropped.save(crop_path)
            art_path = os.path.join(ART_DIR, f"{base}.png")
            cropped.save(art_path)
            print(f"Updated artifact: {art_path}")

print("All v18 verification renders generated successfully!")
