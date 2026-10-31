import subprocess

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
PCB = r"build\icio500\icio500_3d_assembly.kicad_pcb"

renders = [
    ("views/assembly_top_v11.png", ["--side", "top", "--zoom", "0.9"]),
    ("views/assembly_side_left_v11.png", ["--side", "left", "--zoom", "1.0"]),
    ("views/assembly_iso_front_v11.png", ["--rotate", "-35,0,135", "--zoom", "0.85"]),
    ("views/assembly_front_faceplate_v11.png", ["--rotate", "-15,0,45", "--zoom", "0.85"]),
    ("views/assembly_faceplate_direct.png", ["--side", "left", "--zoom", "1.1"]),
]

for out, args in renders:
    cmd = [KICAD_CLI, "pcb", "render"] + args + ["-o", out, PCB]
    print(f"Rendering {out}...")
    subprocess.run(cmd, check=True)
    print(f"Rendered {out}")

print("All v11 views rendered!")
