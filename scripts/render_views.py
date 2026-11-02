import subprocess
import os
import shutil
from PIL import Image

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
PCB = r"build\icio500\icio500_3d_assembly.kicad_pcb"
ART_DIR = r"C:\Users\Chris Williams\.gemini\antigravity\brain\27d96d43-0ba0-4cfa-ba0b-2ac48d075611"

renders = [
    ("views/v16_iso_hero.png", '--rotate "-30,0,135" --zoom 0.85'),
    ("views/v16_iso_brackets.png", '--rotate "-30,0,-45" --zoom 0.85'),
    ("views/v16_top_full.png", '--side top --zoom 0.9'),
]

for out, flags in renders:
    cmd = f'"{KICAD_CLI}" pcb render {flags} -o "{out}" "{PCB}"'
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)
    print(f"Rendered: {out}")

# Autocrop full views
for base in ['v16_iso_hero', 'v16_iso_brackets', 'v16_top_full']:
    src = f"views/{base}.png"
    im = Image.open(src)
    bbox = im.getbbox()
    if bbox:
        cropped = im.crop(bbox)
        crop_path = f"views/{base}_crop.png"
        cropped.save(crop_path)
        art_path = os.path.join(ART_DIR, f"{base}_crop.png")
        shutil.copy(crop_path, art_path)
        print(f"Updated artifact: {art_path}")

# Zoom into U6 / J1 connection on top view:
im_top = Image.open("views/v16_top_full.png")
wt, ht = im_top.size
# Top view has carrier on right, front panel on left, U6/J1 in the middle-left
# Let's crop tight around U6 and J1
# Front edge of carrier is at X ~ 55.39, U6 at X = 68.0, Y = 122.6
crop_u6_top = im_top.crop((int(wt * 0.05), int(ht * 0.40), int(wt * 0.35), int(ht * 0.65)))
crop_u6_top.save("views/v16_u6_top_zoom.png")
shutil.copy("views/v16_u6_top_zoom.png", os.path.join(ART_DIR, "v16_u6_top_zoom.png"))

# Zoom into U6 / J1 connection on iso hero view:
im_hero = Image.open("views/v16_iso_hero.png")
wh, hh = im_hero.size
crop_u6_hero = im_hero.crop((int(wh * 0.15), int(hh * 0.35), int(wh * 0.55), int(hh * 0.70)))
crop_u6_hero.save("views/v16_u6_hero_zoom.png")
shutil.copy("views/v16_u6_hero_zoom.png", os.path.join(ART_DIR, "v16_u6_hero_zoom.png"))

# Zoom into brackets / rear iso:
im_br = Image.open("views/v16_iso_brackets.png")
wb, hb = im_br.size
crop_br = im_br.crop((int(wb * 0.20), int(hb * 0.20), int(wb * 0.80), int(hb * 0.80)))
crop_br.save("views/v16_brackets_zoom.png")
shutil.copy("views/v16_brackets_zoom.png", os.path.join(ART_DIR, "v16_brackets_zoom.png"))

print("All v16 renders and zoom crops generated successfully!")
