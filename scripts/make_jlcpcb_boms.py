import csv

main_meta = {
    "C1": ("220uF", "CP_Elec_6.3x5.4", "C72494"),
    "C3": ("220uF", "CP_Elec_6.3x5.4", "C72494"),
    "C25": ("220uF", "CP_Elec_6.3x5.4", "C72494"),
    "C26": ("220uF", "CP_Elec_6.3x5.4", "C72494"),
    "C27": ("220uF", "CP_Elec_6.3x5.4", "C72494"),
    "C21": ("10uF_BP", "CP_Elec_5x5.4", "UWT1C100MCL1GS"),
    "C22": ("10uF_BP", "CP_Elec_5x5.4", "UWT1C100MCL1GS"),
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
    "R3": ("22k", "R0603", "C22962"),
    "R6": ("22k", "R0603", "C22962"),
    "R8": ("22k", "R0603", "C22962"),
    "R4": ("10k", "R0603", "C25804"),
    "R5": ("10k", "R0603", "C25804"),
    "R7": ("10k", "R0603", "C25804"),
    "R9": ("10R", "R0603", "C22859"),
    "R10": ("10R", "R0603", "C22859"),
    "D1": ("SS14", "D_SMA", "C2480"),
    "D2": ("SS14", "D_SMA", "C2480"),
    "D3": ("1N4148W", "D_SOD-123", "C57759"),
    "D4": ("1N4148W", "D_SOD-123", "C57759"),
    "D5": ("1N4148W", "D_SOD-123", "C57759"),
    "D6": ("1N4148W", "D_SOD-123", "C57759"),
    "D7": ("1N4148W", "D_SOD-123", "C57759"),
    "D8": ("1N4148W", "D_SOD-123", "C57759"),
    "D9": ("1N4148W", "D_SOD-123", "C57759"),
    "D10": ("1N4148W", "D_SOD-123", "C57759"),
    "U1": ("TSR1-2450", "TO-220-3_Vertical", "TSR1-2450"),
    "U2": ("THAT1200S08-U", "SOIC-8_3.9x4.9mm_P1.27mm", "THAT1200S08-U"),
    "U3": ("TL072CDT", "SOIC-8_3.9x4.9mm_P1.27mm", "C9002"),
    "U4": ("THAT1646S08-U", "SOIC-8_3.9x4.9mm_P1.27mm", "THAT1646S08-U"),
    "U5": ("Daisy_Seed_Socket", "DIP-40_W15.24mm_Socket", ""),
    "U6": ("PinHeader_2x10_P2.54mm_Horizontal", "PinHeader_2x10_P2.54mm_Horizontal", "C124378"),
}

# 1. Update build/jlcpcb/icio500_cpl.csv with real values and remove PCB edge finger J1 from CPL
rows = []
with open("build/jlcpcb/icio500_cpl.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        ref = r["Ref"]
        if ref == "J1":
            continue  # Gold finger edge connector is part of PCB fabrication, not SMT placement
        if ref in main_meta:
            r["Val"] = main_meta[ref][0]
        rows.append(r)

with open("build/jlcpcb/icio500_cpl.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Ref", "Val", "Package", "PosX", "PosY", "Rot", "Side"], quoting=csv.QUOTE_NONNUMERIC)
    # Write header unquoted to match KiCad standard
    f.write("Ref,Val,Package,PosX,PosY,Rot,Side\n")
    for r in rows:
        f.write(f'"{r["Ref"]}","{r["Val"]}","{r["Package"]}",{r["PosX"]},{r["PosY"]},{r["Rot"]},{r["Side"]}\n')

# 2. Write build/jlcpcb/icio500_bom.csv grouped by (Comment, Footprint, LCSC Part #)
from collections import defaultdict
groups = defaultdict(list)
for ref, (val, fp, lcsc) in main_meta.items():
    groups[(val, fp, lcsc)].append(ref)

with open("build/jlcpcb/icio500_bom.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for (val, fp, lcsc), refs in groups.items():
        w.writerow([val, ",".join(refs), fp, lcsc])

# 3. Write build/jlcpcb/panel_satellite_bom.csv
sat_groups = [
    ("WP-SMRA-M3 (Wuerth 7466303)", "BR1,BR2", "Mounting_Wuerth_WP-SMRA-M3_L7mm_7466303_Horizontal", "7466303"),
    ("10uF", "C1", "C_0402_1005Metric", "C15849"),
    ("100nF", "C2", "C_0402_1005Metric", "C1525"),
    ("BLM18PG", "FB1", "L_0402_1005Metric", "C76886"),
    ("PinSocket_2x10_P2.54mm_Vertical_SMD", "J1", "PinSocket_2x10_P2.54mm_Vertical_SMD", "C2906163"),
    ("33R", "R1,R2,R3,R4,R5,R6,R7,R8,R9,R10", "R_0402_1005Metric", "C25105"),
    ("4.7k", "R11,R12", "R_0402_1005Metric", "C25900"),
    ("IS31FL3236", "U1", "TSSOP-36_6.1x12.5mm_P0.65mm", "C282734"),
    ("LED", "D1,D2,D3,D4,D5,D6,D7,D8,D9,D10", "LED_0805_2012Metric", "C2290"),
    ("EC11E", "ENC1", "RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm", "C470661"),
]
with open("build/jlcpcb/panel_satellite_bom.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for row in sat_groups:
        w.writerow(row)

print("Generated build/jlcpcb/icio500_bom.csv and build/jlcpcb/panel_satellite_bom.csv")
