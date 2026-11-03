import os
import shutil
import subprocess
import zipfile

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
OUT_ROOT = "build/jlcpcb"

# Clear out any previous files in OUT_ROOT
if os.path.exists(OUT_ROOT):
    shutil.rmtree(OUT_ROOT)
os.makedirs(OUT_ROOT, exist_ok=True)

boards = [
    ("carrier", "build/icio500/icio500.kicad_pcb", "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts"),
    ("faceplate", "build/icio500/faceplate_front.kicad_pcb", "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Dwgs.User,Cmts.User,Edge.Cuts"),
    ("encoder", "build/icio500/encoder_board.kicad_pcb", "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Dwgs.User,Cmts.User,Edge.Cuts"),
]

for name, pcb_path, layers in boards:
    # 1. Dedicated board directory
    board_dir = os.path.join(OUT_ROOT, name)
    os.makedirs(board_dir, exist_ok=True)

    # 2. Temporary gerbers staging directory
    stage_dir = os.path.join(board_dir, "temp_gerbers")
    os.makedirs(stage_dir, exist_ok=True)

    # Export Gerbers (standard RS-274X without X2 %TO attributes for exact JLCPCB SMT coordinates)
    subprocess.run([
        KICAD_CLI, "pcb", "export", "gerbers",
        "--layers", layers,
        "--use-drill-file-origin",
        "--no-protel-ext",
        "--no-x2",
        "-o", stage_dir + "/",
        pcb_path
    ], check=True)

    # Export Excellon Drill + Map
    subprocess.run([
        KICAD_CLI, "pcb", "export", "drill",
        "--format", "excellon",
        "--excellon-units", "mm",
        "--excellon-zeros-format", "decimal",
        "--excellon-oval-format", "route",
        "--drill-origin", "plot",
        "--generate-map",
        "--map-format", "gerberx2",
        "-o", stage_dir + "/",
        pcb_path
    ], check=True)

    # Export Component Position (CPL / Pick-and-Place CSV)
    pos_csv = os.path.join(board_dir, f"{name}_cpl.csv")
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

    # Zip Gerbers + Drills into clean package
    zip_path = os.path.join(board_dir, f"{name}_gerbers.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fn in sorted(os.listdir(stage_dir)):
            full = os.path.join(stage_dir, fn)
            if os.path.isfile(full):
                zf.write(full, arcname=fn)
    
    # Remove raw loose gerbers staging folder (keep only the zip archive!)
    shutil.rmtree(stage_dir)

    # Also place top-level copies in build/jlcpcb/
    shutil.copyfile(zip_path, os.path.join(OUT_ROOT, f"{name}_gerbers.zip"))
    shutil.copyfile(pos_csv, os.path.join(OUT_ROOT, f"{name}_cpl.csv"))

    print(f"Exported {name}: {zip_path} and {pos_csv}")

print("JLCPCB exports complete.")
