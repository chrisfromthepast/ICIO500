import subprocess
import os

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
PCB = r"build\icio500\icio500_3d_assembly.kicad_pcb"

renders = [
    ("views/assembly_top_v10.png", "--side top --zoom 0.9"),
    ("views/assembly_side_left_v10.png", "--side left --zoom 1.0"),
    ("views/assembly_iso_front_v10.png", '--rotate "-35,0,135" --zoom 0.85'),
    ("views/assembly_front_faceplate_v10.png", '--rotate "-15,0,45" --zoom 0.85'),
]

for out, flags in renders:
    cmd = f'"{KICAD_CLI}" pcb render {flags} -o "{out}" "{PCB}"'
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)
    print(f"Rendered: {out}")

print("All assembly v10 views rendered successfully!")
