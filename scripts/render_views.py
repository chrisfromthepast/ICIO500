"""
Render verified 3D views of the ICIO500 modular satellite assemblies into renders/
and copy key showcase images to the artifact directory.

Usage:
  python scripts/render_views.py               # Render all 9 views
  python scripts/render_views.py --only front  # Render only front showcase views
  python scripts/render_views.py --only wood   # Render all 5 Wood assembly views
"""

import argparse
import os
import subprocess
from PIL import Image

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
WOOD_ASSY = r"kicad\icio500_satellite_wood_3d.kicad_pcb"
ACRYLIC_ASSY = r"kicad\icio500_satellite_acrylic_3d.kicad_pcb"
SAT_PCB = r"kicad\faceplate_satellite.kicad_pcb"
ART_DIR = r"C:\Users\Chris Williams\.gemini\antigravity\brain\27d96d43-0ba0-4cfa-ba0b-2ac48d075611"

# Each entry: (tag, pcb_path, out_path, kicad_flags, post_transpose)
RENDERS = [
    # Front-facing showcase views (--only front)
    ("front", WOOD_ASSY,    "renders/satellite_wood_iso_front.png",      '--quality high --perspective --rotate "-58,0,78" --zoom 0.65', None),
    ("front", WOOD_ASSY,    "renders/satellite_wood_front_upright.png",  '--quality high --side left --zoom 0.95', Image.ROTATE_270),
    ("front", ACRYLIC_ASSY, "renders/satellite_acrylic_iso_front.png",   '--quality high --perspective --rotate "-58,0,78" --zoom 0.65', None),
    ("front", ACRYLIC_ASSY, "renders/satellite_acrylic_front_upright.png", '--quality high --side left --zoom 0.95', Image.ROTATE_270),
    ("front", ACRYLIC_ASSY, "renders/satellite_acrylic_top_edge.png",    '--quality high --side back --zoom 1.45 --pivot "-7.2,0,0.8"', None),
    # Engineering clearance & rear views
    ("tech",  WOOD_ASSY,    "renders/satellite_wood_top_edge.png",       '--quality high --side back --zoom 1.45 --pivot "-7.2,0,0.8"', None),
    ("tech",  WOOD_ASSY,    "renders/satellite_wood_side_stackup.png",  '--quality high --side top --zoom 3.5 --pivot "-8.5,-4.3,0"', None),
    ("tech",  WOOD_ASSY,    "renders/satellite_wood_rear.png",           '--quality high --perspective --rotate "-30,0,-45" --zoom 0.90', None),
    ("tech",  SAT_PCB,      "renders/satellite_pcb_rear.png",            '--quality high --side bottom --zoom 0.95', None),
]

ARTIFACT_COPIES = {
    "renders/satellite_wood_iso_front.png",
    "renders/satellite_wood_front_upright.png",
    "renders/satellite_wood_top_edge.png",
    "renders/satellite_acrylic_iso_front.png",
    "renders/satellite_acrylic_front_upright.png",
    "renders/satellite_acrylic_top_edge.png",
}


def run():
    parser = argparse.ArgumentParser(description="Render ICIO500 3D views.")
    parser.add_argument("--only", choices=["all", "front", "tech", "wood"], default="all")
    args = parser.parse_args()

    os.makedirs("renders", exist_ok=True)
    for tag, pcb, out_path, flags, transpose_op in RENDERS:
        if args.only == "wood":
            if pcb != WOOD_ASSY:
                continue
        elif args.only != "all" and tag != args.only:
            continue
        cmd = f'"{KICAD_CLI}" pcb render {flags} -w 1800 -h 1200 -o "{out_path}" "{pcb}"'
        print(f"Rendering {out_path} ...")
        subprocess.run(cmd, shell=True, check=True)
        with Image.open(out_path) as im:
            if transpose_op is not None:
                im = im.transpose(transpose_op)
            bbox = im.getbbox()
            if bbox:
                pad = 24
                w, h = im.size
                crop_box = (
                    max(0, bbox[0] - pad),
                    max(0, bbox[1] - pad),
                    min(w, bbox[2] + pad),
                    min(h, bbox[3] + pad),
                )
                im_crop = im.crop(crop_box)
            else:
                im_crop = im
            bg = Image.new("RGB", im_crop.size, (248, 250, 252))
            if im_crop.mode == "RGBA":
                bg.paste(im_crop, mask=im_crop.split()[3])
            else:
                bg.paste(im_crop)
            bg.save(out_path, optimize=True)
        if out_path in ARTIFACT_COPIES and os.path.isdir(ART_DIR):
            art_dst = os.path.join(ART_DIR, os.path.basename(out_path))
            with Image.open(out_path) as im_art:
                im_art.save(art_dst)
            print(f"  Copied artifact: {art_dst}")
    print("Selected satellite 3D renders completed!")


if __name__ == "__main__":
    run()
