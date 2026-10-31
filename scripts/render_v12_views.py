import subprocess
import os
import shutil
from PIL import Image
import numpy as np

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
PCB = r"build\icio500\icio500_3d_assembly.kicad_pcb"
ART_DIR = r"C:\Users\Chris Williams\.gemini\antigravity\brain\27d96d43-0ba0-4cfa-ba0b-2ac48d075611"

renders = [
    ("views/assembly_top_v12.png", ["--side", "top", "--zoom", "0.9"]),
    ("views/assembly_side_left_v12.png", ["--rotate", "0,-90,0", "--zoom", "0.9"]),
    ("views/assembly_iso_front_left_v12.png", ["--rotate", "-25,-45,35", "--zoom", "0.85"]),
    ("views/assembly_iso_front_right_v12.png", ["--rotate", "-25,45,-35", "--zoom", "0.85"]),
    ("views/assembly_iso_hero_v12.png", ["--rotate", "-35,0,135", "--zoom", "0.85"]),
    ("views/assembly_front_faceplate_v12.png", ["--rotate", "0,-90,90", "--zoom", "1.1"]),
]

for out, args in renders:
    cmd = [KICAD_CLI, "pcb", "render"] + args + ["-o", out, PCB]
    print(f"Rendering {out}...")
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    print(f"Rendered {out}")
    
    # Auto-crop
    im = Image.open(out).convert('RGB')
    arr = np.array(im)
    mask = (arr > 25).any(axis=2)
    ys, xs = np.where(mask)
    if len(xs) > 0:
        cropped = im.crop((
            max(0, xs.min() - 15),
            max(0, ys.min() - 15),
            min(im.size[0], xs.max() + 15),
            min(im.size[1], ys.max() + 15)
        ))
        crop_path = out.replace('.png', '_crop.png')
        cropped.save(crop_path)
        base = os.path.basename(crop_path)
        art_path = os.path.join(ART_DIR, base)
        shutil.copy(crop_path, art_path)
        print(f"Saved and copied {base} ({cropped.size})")

print("All v12 views rendered and cropped successfully!")
