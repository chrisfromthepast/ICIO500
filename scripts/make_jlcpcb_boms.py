import csv
import os
import shutil
from collections import defaultdict

# -------------------------------------------------------------
# 1. Carrier Card (icio500) Metadata & Position Overrides
# -------------------------------------------------------------
main_meta = {
    "C1": ("220uF", "CP_Elec_6.3x5.4", "C4747974"),
    "C3": ("220uF", "CP_Elec_6.3x5.4", "C4747974"),
    "C25": ("220uF", "CP_Elec_6.3x5.4", "C4747974"),
    "C26": ("220uF", "CP_Elec_6.3x5.4", "C4747974"),
    "C27": ("220uF", "CP_Elec_6.3x5.4", "C4747974"),
    "C21": ("10uF_BP", "CP_Elec_5x5.4", "C1984751"),
    "C22": ("10uF_BP", "CP_Elec_5x5.4", "C1984751"),
    "C2": ("100nF", "C0603", "C14663"),
    "C4": ("100nF", "C0603", "C14663"),
    "C6": ("100nF", "C0603", "C14663"),
    "C7": ("100nF", "C0603", "C14663"),
    "C8": ("100nF", "C0603", "C14663"),
    "C15": ("100nF", "C0603", "C14663"),
    "C16": ("100nF", "C0603", "C14663"),
    "C23": ("100nF", "C0603", "C14663"),
    "C24": ("100nF", "C0603", "C14663"),
    "C5": ("10uF", "C0603", "C19702"),
    "C12": ("10uF", "C0603", "C19702"),
    "C13": ("10uF", "C0603", "C19702"),
    "C14": ("10uF", "C0603", "C19702"),
    "C17": ("47pF", "C0603", "C1671"),
    "C18": ("47pF", "C0603", "C1671"),
    "C9": ("220pF", "C0402", "C1530"),
    "C10": ("220pF", "C0402", "C1530"),
    "C11": ("220pF", "C0402", "C1530"),
    "C19": ("1uF", "C0402", "C52923"),
    "C20": ("1uF", "C0402", "C52923"),
    "R1": ("100R", "R0603", "C22775"),
    "R2": ("100R", "R0603", "C22775"),
    "R3": ("22k", "R0603", "C31850"),
    "R6": ("22k", "R0603", "C31850"),
    "R8": ("22k", "R0603", "C31850"),
    "R4": ("10k", "R0603", "C25804"),
    "R5": ("10k", "R0603", "C25804"),
    "R7": ("10k", "R0603", "C25804"),
    "R9": ("10R", "R0603", "C22859"),
    "R10": ("10R", "R0603", "C22859"),
    "D1": ("SS14", "D_SMA", "C2480"),
    "D2": ("SS14", "D_SMA", "C2480"),
    "D3": ("1N4148W", "D_SOD-123", "C81598"),
    "D4": ("1N4148W", "D_SOD-123", "C81598"),
    "D5": ("1N4148W", "D_SOD-123", "C81598"),
    "D6": ("1N4148W", "D_SOD-123", "C81598"),
    "D7": ("1N4148W", "D_SOD-123", "C81598"),
    "D8": ("1N4148W", "D_SOD-123", "C81598"),
    "D9": ("1N4148W", "D_SOD-123", "C81598"),
    "D10": ("1N4148W", "D_SOD-123", "C81598"),
    "U1": ("TSR 1-2450", "Converter_DCDC_TRACO_TSR-1_THT", "C6886877"),
    "U2": ("1200S08-U", "SOIC-8_3.9x4.9mm_P1.27mm", "C3202799"),
    "U3": ("TL072CDT", "SOIC-8_3.9x4.9mm_P1.27mm", "C6961"),
    "U4": ("THAT1646S08-U", "SOIC-8_3.9x4.9mm_P1.27mm", "C5290156"),
    "U5": ("Daisy_Seed_Socket", "DIP-40_W15.24mm_Socket", "C2332"),
    "U6": ("2541WR-2x10P", "PinHeader_2x10_P2.54mm_Horizontal", "C5383093"),
}

main_pos_override = {
    "U1": ("163.307000", "-145.485500", "180.000000"),
    "U5": ("102.620000", "-114.130000", "270.000000"),
    "U6": ("66.730000", "-111.175000", "90.000000"),
}

# -------------------------------------------------------------
# 2. Active 2.0 mm Faceplate Metadata
# -------------------------------------------------------------
faceplate_groups = [
    ("WP-SMRA-M3", "BR1,BR2", "Mounting_Wuerth_WP-SMRA-M3_L7mm_7466303_Horizontal", "C5523891"),
    ("10uF", "C1", "C_0402_1005Metric", "C15525"),
    ("100nF", "C2", "C_0402_1005Metric", "C1525"),
    ("BLM15AX601SN1D", "FB1", "L_0402_1005Metric", "C76886"),
    ("Conn_02x10_Odd_Even", "J1", "PinSocket_2x10_P2.54mm_Vertical_SMD", "C41427539"),
    ("Conn_01x05_Female", "J2", "PinSocket_1x05_P2.54mm_Vertical_SMD_Pin1Left", "C2898748"),
    ("33R", "R1,R2,R3,R4,R5,R6,R7,R8,R9,R10", "R_0402_1005Metric", "C25105"),
    ("4.7k", "R11,R12", "R_0402_1005Metric", "C25900"),
    ("PCA9555PW", "U1", "TSSOP-24_4.4x7.8mm_P0.65mm", "C128392"),
    ("LED_RED", "D1", "LED_0805_2012Metric", "C2295"),
    ("LED_YLW", "D2,D3", "LED_0805_2012Metric", "C2296"),
    ("LED_GRN", "D4,D5,D6,D7,D8,D9,D10", "LED_0805_2012Metric", "C2297"),
]

faceplate_meta = {}
for comment, refs_str, fp, lcsc in faceplate_groups:
    for r in refs_str.split(","):
        faceplate_meta[r.strip()] = (comment, fp, lcsc)

# -------------------------------------------------------------
# 3. Encoder Daughtercard Metadata
# -------------------------------------------------------------
encoder_groups = [
    ("PEC11R-4020F-S0024", "ENC1", "RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm", "C255515"),
    ("Conn_01x05_Male", "P1", "PinHeader_1x05_P2.54mm_Vertical_SMD_Pin1Left", "C224368"),
]

encoder_meta = {}
for comment, refs_str, fp, lcsc in encoder_groups:
    for r in refs_str.split(","):
        encoder_meta[r.strip()] = (comment, fp, lcsc)

# -------------------------------------------------------------
# CPL Conversion Function
# -------------------------------------------------------------
def convert_cpl_to_jlcpcb(cpl_path, meta_override=None, pos_override=None, exclude_refs=None):
    if not os.path.exists(cpl_path):
        return
    exclude_refs = exclude_refs or set()
    pos_override = pos_override or {}
    rows = []
    with open(cpl_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            ref = r.get("Ref") or r.get("Designator", "")
            if not ref or ref in exclude_refs:
                continue
            val = r.get("Val", "")
            pkg = r.get("Package", "")
            if meta_override and ref in meta_override:
                val = meta_override[ref][0]
                pkg = meta_override[ref][1]
            pos_x = r.get("PosX") or r.get("Mid X", "")
            pos_y = r.get("PosY") or r.get("Mid Y", "")
            rot = r.get("Rot") or r.get("Rotation", "")
            if ref in pos_override:
                pos_x, pos_y, rot = pos_override[ref]
            side = (r.get("Side") or r.get("Layer", "")).lower()
            rows.append((ref, val, pkg, pos_x, pos_y, rot, side))

    with open(cpl_path, "w", newline="", encoding="utf-8") as f:
        f.write("Designator,Val,Package,Mid X,Mid Y,Rotation,Layer\n")
        for ref, val, pkg, pos_x, pos_y, rot, side in rows:
            f.write(f"{ref},{val},{pkg},{pos_x},{pos_y},{rot},{side}\n")

# Process CPLs
convert_cpl_to_jlcpcb("build/jlcpcb/icio500_cpl.csv", meta_override=main_meta, pos_override=main_pos_override, exclude_refs={"J1"})
convert_cpl_to_jlcpcb("build/jlcpcb/faceplate_front_cpl.csv", meta_override=faceplate_meta)
convert_cpl_to_jlcpcb("build/jlcpcb/encoder_board_cpl.csv", meta_override=encoder_meta)

# Write BOMs
# 1. Carrier Card
groups = defaultdict(list)
for ref, (val, fp, lcsc) in main_meta.items():
    groups[(val, fp, lcsc)].append(ref)

with open("build/jlcpcb/icio500_bom.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for (val, fp, lcsc), refs in groups.items():
        w.writerow([val, ",".join(refs), fp, lcsc])

# 2. Active Faceplate
with open("build/jlcpcb/faceplate_front_bom.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for row in faceplate_groups:
        w.writerow(row)

# 3. Encoder Daughtercard
with open("build/jlcpcb/encoder_board_bom.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for row in encoder_groups:
        w.writerow(row)

# Create standard, intuitive alias filenames (so users and fab can find both faceplate_cpl.csv and faceplate_front_cpl.csv)
aliases = [
    ("faceplate_front_cpl.csv", "faceplate_cpl.csv"),
    ("faceplate_front_bom.csv", "faceplate_bom.csv"),
    ("faceplate_front_jlcpcb_gerbers.zip", "faceplate_jlcpcb_gerbers.zip"),
    ("icio500_cpl.csv", "carrier_cpl.csv"),
    ("icio500_bom.csv", "carrier_bom.csv"),
    ("icio500_jlcpcb_gerbers.zip", "carrier_jlcpcb_gerbers.zip"),
    ("encoder_board_cpl.csv", "encoder_cpl.csv"),
    ("encoder_board_bom.csv", "encoder_bom.csv"),
    ("encoder_board_jlcpcb_gerbers.zip", "encoder_jlcpcb_gerbers.zip"),
]
for src, dst in aliases:
    s_path = os.path.join("build/jlcpcb", src)
    d_path = os.path.join("build/jlcpcb", dst)
    if os.path.exists(s_path):
        shutil.copyfile(s_path, d_path)

print("Generated build/jlcpcb production packages with dual standard names successfully!")
