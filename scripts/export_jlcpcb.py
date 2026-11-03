import os
import shutil
import subprocess
import zipfile

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
OUT_ROOT = "build/jlcpcb"
os.makedirs(OUT_ROOT, exist_ok=True)

boards = [
    ("icio500", "build/icio500/icio500.kicad_pcb", "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts"),
    ("faceplate_front", "build/icio500/faceplate_front.kicad_pcb", "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Dwgs.User,Cmts.User,Edge.Cuts"),
    ("encoder_board", "build/icio500/encoder_board.kicad_pcb", "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Dwgs.User,Cmts.User,Edge.Cuts"),
]

for name, pcb_path, layers in boards:
    bdir = os.path.join(OUT_ROOT, name)
    if os.path.exists(bdir):
        shutil.rmtree(bdir)
    os.makedirs(bdir, exist_ok=True)

    # 1. Export Gerbers (standard RS-274X without X2 %TO attributes so JLCPCB uses CPL exact coordinates/rotations)
    subprocess.run([
        KICAD_CLI, "pcb", "export", "gerbers",
        "--layers", layers,
        "--use-drill-file-origin",
        "--no-protel-ext",
        "--no-x2",
        "-o", bdir + "/",
        pcb_path
    ], check=True)

    # 2. Export Excellon Drill + Map
    subprocess.run([
        KICAD_CLI, "pcb", "export", "drill",
        "--format", "excellon",
        "--excellon-units", "mm",
        "--excellon-zeros-format", "decimal",
        "--excellon-oval-format", "route",
        "--drill-origin", "plot",
        "--generate-map",
        "--map-format", "gerberx2",
        "-o", bdir + "/",
        pcb_path
    ], check=True)

    # 3. Export Component Position (CPL / Pick-and-Place CSV) and convert headers to JLCPCB standard
    pos_csv = os.path.join(OUT_ROOT, f"{name}_cpl.csv")
    subprocess.run([
        KICAD_CLI, "pcb", "export", "pos",
        "--side", "both",
        "--format", "csv",
        "--units", "mm",
        "--use-drill-file-origin",
        "-o", pos_csv,
        pcb_path
    ], check=True)

    with open(pos_csv, "r", encoding="utf-8") as f:
        cpl_text = f.read()
    cpl_text = cpl_text.replace("Ref,Val,Package,PosX,PosY,Rot,Side", "Designator,Val,Package,Mid X,Mid Y,Rotation,Layer", 1)
    with open(pos_csv, "w", encoding="utf-8", newline="") as f:
        f.write(cpl_text)

    # 4. Zip Gerbers + Drills for direct JLCPCB upload
    zip_path = os.path.join(OUT_ROOT, f"{name}_jlcpcb_gerbers.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fn in sorted(os.listdir(bdir)):
            full = os.path.join(bdir, fn)
            if os.path.isfile(full):
                zf.write(full, arcname=fn)
    print(f"Exported {zip_path} ({os.path.getsize(zip_path)} bytes) and {pos_csv}")
