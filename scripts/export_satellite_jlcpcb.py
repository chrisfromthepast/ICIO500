"""
Export JLCPCB Gerber, Drill, BOM, and CPL deliverables exclusively for the 0.8 mm 2-layer
Satellite Active PCB (kicad/faceplate_satellite.kicad_pcb) into:
  fabrication/satellite_faceplate/jlcpcb_satellite_pcb/

Does NOT touch in_production/ or archived_v1_blind_slot/ packages.
"""

import csv
import os
import shutil
import subprocess
import zipfile

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
PCB_PATH = "kicad/faceplate_satellite.kicad_pcb"
OUT_DIR = "fabrication/satellite_faceplate/jlcpcb_satellite_pcb"

SATELLITE_GROUPS = [
    ("WP-SMRA-M3",          "BR1,BR2", "Mounting_Wuerth_WP-SMRA-M3_L7mm_7466303_Horizontal", "C5523891"),
    ("100nF",               "C1",      "C_0402_1005Metric",                                  "C1525"),
    ("10uF",                "C2",      "C_0402_1005Metric",                                  "C15525"),
    ("BLM15AX601SN1D",      "FB1",     "L_0402_1005Metric",                                  "C76886"),
    ("Conn_02x10_Odd_Even", "J1",      "PinSocket_2x10_P2.54mm_Vertical_SMD",                "C41427539"),
    ("68R",                 "R1",      "R_0402_1005Metric",                                  "C25131"),
    ("82R",                 "R2,R3",   "R_0402_1005Metric",                                  "C25136"),
    ("100R", "R4,R5,R6,R7,R8,R9,R10,R16,R17,R18,R19,R20,R21", "R_0402_1005Metric",           "C25076"),
    ("4.7k",                "R11,R12", "R_0402_1005Metric",                                  "C25900"),
    ("PCA9555PW",           "U1",      "TSSOP-24_4.4x7.8mm_P0.65mm",                         "C128392"),
    ("XL-3216SURC-FB",      "D1,D11,D14",                   "LED_1206_3216Metric_ReverseMount_Hole1.8x2.4mm", "C3646938"),
    ("XL-3216UYC-FB",       "D2,D3",                        "LED_1206_3216Metric_ReverseMount_Hole1.8x2.4mm", "C3646939"),
    ("XL-3216UGC-FB",       "D4,D5,D6,D7,D8,D9,D10,D12,D15","LED_1206_3216Metric_ReverseMount_Hole1.8x2.4mm", "C3646937"),
    ("XL-3216UBC-FB",       "D13,D16",                      "LED_1206_3216Metric_ReverseMount_Hole1.8x2.4mm", "C3646941"),
]

# Verified KiCad->JLCPCB bottom TSSOP-24 orientation matching commit 8614cab
POS_OVERRIDE = {
    "U1": ("31.800000", "-52.000000", "270.000000"),
}

EXCLUDE_REFS = {"MH_TOP_L", "MH_TOP_R"}


def run():
    if os.path.exists(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR, exist_ok=True)
    stage_dir = os.path.join(OUT_DIR, "temp_gerbers")
    os.makedirs(stage_dir, exist_ok=True)

    # 1. Export Gerbers (standard 2-layer RS-274X without X2 attributes)
    subprocess.run([
        KICAD_CLI, "pcb", "export", "gerbers",
        "--layers", "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts",
        "--use-drill-file-origin",
        "--no-protel-ext",
        "--no-x2",
        "-o", stage_dir + "/",
        PCB_PATH,
    ], check=True)

    # 2. Export Excellon Drills
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
        PCB_PATH,
    ], check=True)

    # 3. Export CPL & Format to JLCPCB standard
    cpl_path = os.path.join(OUT_DIR, "faceplate_satellite_cpl.csv")
    subprocess.run([
        KICAD_CLI, "pcb", "export", "pos",
        "--side", "both",
        "--format", "csv",
        "--units", "mm",
        "--use-drill-file-origin",
        "-o", cpl_path,
        PCB_PATH,
    ], check=True)

    meta = {}
    for comment, refs_str, fp, lcsc in SATELLITE_GROUPS:
        for r in refs_str.split(","):
            meta[r.strip()] = (comment, fp, lcsc)

    rows = []
    with open(cpl_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            ref = (r.get("Ref") or r.get("Designator", "")).strip()
            if not ref or ref in EXCLUDE_REFS:
                continue
            val = r.get("Val", "")
            pkg = r.get("Package", "")
            if ref in meta:
                val, pkg, _ = meta[ref]
            px = r.get("PosX") or r.get("Mid X", "")
            py = r.get("PosY") or r.get("Mid Y", "")
            rot = r.get("Rot") or r.get("Rotation", "")
            if ref in POS_OVERRIDE:
                px, py, rot = POS_OVERRIDE[ref]
            side = (r.get("Side") or r.get("Layer", "")).lower()
            rows.append((ref, val, pkg, px, py, rot, side))

    with open(cpl_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Val", "Package", "Mid X", "Mid Y", "Rotation", "Layer"])
        for row in rows:
            w.writerow(row)

    # 4. Write BOM
    bom_path = os.path.join(OUT_DIR, "faceplate_satellite_bom.csv")
    with open(bom_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for row in SATELLITE_GROUPS:
            w.writerow(row)

    # 5. Zip Gerbers + Drill
    zip_path = os.path.join(OUT_DIR, "faceplate_satellite_gerbers.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fn in sorted(os.listdir(stage_dir)):
            full = os.path.join(stage_dir, fn)
            if os.path.isfile(full):
                zf.write(full, arcname=fn)
    shutil.rmtree(stage_dir)

    print(f"Exported JLCPCB satellite package cleanly to {OUT_DIR}:")
    print(f"  Gerbers: {zip_path} ({os.path.getsize(zip_path)} B)")
    print(f"  BOM:     {bom_path} ({len(SATELLITE_GROUPS)} unique rows)")
    print(f"  CPL:     {cpl_path} ({len(rows)} components)")


if __name__ == "__main__":
    run()
