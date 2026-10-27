import json
import re
import subprocess

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"

print("=" * 60)
print("VPR-500 MECHANICAL & ELECTRICAL VERIFICATION AUDIT")
print("=" * 60)

# 1. Main PCB dimensions and features
with open("build/icio500/icio500.kicad_pcb", "r", encoding="utf-8") as f:
    main_pcb = f.read()

# Parse Edge.Cuts
ec_matches = re.findall(r'\(gr_line\s+\(start\s+([-\d.]+)\s+([-\d.]+)\)\s+\(end\s+([-\d.]+)\s+([-\d.]+)\).*?\"Edge\.Cuts\"', main_pcb, re.DOTALL)
xs = [float(p[0]) for p in ec_matches] + [float(p[2]) for p in ec_matches]
ys = [float(p[1]) for p in ec_matches] + [float(p[3]) for p in ec_matches]

x_min, x_max = min(xs), max(xs)
y_min, y_max = min(ys), max(ys)
card_depth_mm = x_max - x_min
card_depth_in = card_depth_mm / 25.4
card_height_mm = y_max - y_min
card_height_in = card_height_mm / 25.4

# Total module depth with 3.20 mm front panel sandwich (1.6 mm faceplate + 1.6 mm satellite)
total_module_depth_mm = card_depth_mm + 3.20
total_module_depth_in = total_module_depth_mm / 25.4

print(f"Main PCB Dimensions:")
print(f"  Front Edge X: {x_min:.2f} mm | Rear Tip X: {x_max:.2f} mm")
print(f"  Carrier Card Depth: {card_depth_mm:.2f} mm ({card_depth_in:.3f}\")")
print(f"  Total Module Depth (w/ 3.2mm panel): {total_module_depth_mm:.2f} mm ({total_module_depth_in:.3f}\") [VPR Spec: 5.938\" +/- 0.02\"]")
print(f"  Card Height: {card_height_mm:.2f} mm ({card_height_in:.3f}\") [VPR Spec: 4.500\"]")

# Check Chamfers
has_top_chamfer = any(abs(float(p[0]) - 202.0) < 0.1 and abs(float(p[2]) - 203.0) < 0.1 for p in ec_matches)
has_bot_chamfer = any(abs(float(p[0]) - 203.0) < 0.1 and abs(float(p[2]) - 202.0) < 0.1 for p in ec_matches)
print(f"  Tongue Lead-in 45 deg Chamfers: {'PASS' if (has_top_chamfer and has_bot_chamfer) else 'FAIL'}")

# Check MH1, MH2, U6
def get_fp_at(text, ref):
    idx = text.find(f'Reference "{ref}"')
    if idx == -1: idx = text.find(f'Reference" "{ref}"')
    if idx == -1: return None
    start = text.rfind('(footprint', 0, idx)
    m = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)', text[start:start+400])
    return (float(m.group(1)), float(m.group(2))) if m else None

mh1 = get_fp_at(main_pcb, "MH1")
mh2 = get_fp_at(main_pcb, "MH2")
u6 = get_fp_at(main_pcb, "U6")
print(f"  Mounting Hole MH1: at {mh1} (expected X=58.39, Y=60.00)")
print(f"  Mounting Hole MH2: at {mh2} (expected X=58.39, Y=155.00)")
print(f"  Right-angle Header U6: at {u6} (expected X=59.22, Y=120.475)")

# Check Satellite board
with open("build/icio500/panel_satellite.kicad_pcb", "r", encoding="utf-8") as f:
    sat_pcb = f.read()

br1 = get_fp_at(sat_pcb, "BR1")
br2 = get_fp_at(sat_pcb, "BR2")
j1 = get_fp_at(sat_pcb, "J1")
print(f"\nSatellite PCB Components:")
print(f"  SMD Bracket BR1: at {br1}")
print(f"  SMD Bracket BR2: at {br2}")
print(f"  SMD Socket J1:   at {j1}")

# Check concentricity and mating
# Satellite Y = Main Y + 54.525 mm
sat_y_offset = 54.525
br1_matched = abs(br1[1] - (mh1[1] + sat_y_offset)) < 0.01
br2_matched = abs(br2[1] - (mh2[1] + sat_y_offset)) < 0.01
j1_matched = abs(j1[1] - (u6[1] + sat_y_offset)) < 0.01

print(f"\nMechanical Alignment & Concentricity:")
print(f"  MH1 <-> BR1 Concentricity: {'100% PERFECT MATCH' if br1_matched else 'MISMATCH'}")
print(f"  MH2 <-> BR2 Concentricity: {'100% PERFECT MATCH' if br2_matched else 'MISMATCH'}")
print(f"  U6 <-> J1 Connector Mating: {'100% PERFECT MATCH' if j1_matched else 'MISMATCH'}")

# DRC check
print("\n" + "=" * 60)
print("ELECTRICAL DESIGN RULES CHECK (DRC)")
print("=" * 60)
boards = [
    ("Main Board (icio500.kicad_pcb)", "build/icio500/icio500.kicad_pcb"),
    ("Satellite Board (panel_satellite.kicad_pcb)", "build/icio500/panel_satellite.kicad_pcb"),
    ("Faceplate (faceplate_front.kicad_pcb)", "build/icio500/faceplate_front.kicad_pcb"),
]

for name, path in boards:
    res = subprocess.run([
        KICAD_CLI, "pcb", "drc",
        "--format", "json",
        "--output", "temp_audit_drc.json",
        path
    ], capture_output=True, text=True)
    with open("temp_audit_drc.json", "r", encoding="utf-8") as f:
        d = json.load(f)
    vios = d.get("violations", [])
    unconn = d.get("unconnected_items", [])
    non_lib = [v for v in vios if "lib_footprint" not in v.get("type", "")]
    print(f"{name}:")
    print(f"  Unconnected Items: {len(unconn)}")
    print(f"  Electrical / Clearance DRC Violations: {len(non_lib)}")
    print(f"  Status: {'CLEAN / PRODUCTION READY' if len(unconn) == 0 and len(non_lib) == 0 else 'ERRORS FOUND'}")

import os
if os.path.exists("temp_audit_drc.json"): os.remove("temp_audit_drc.json")
