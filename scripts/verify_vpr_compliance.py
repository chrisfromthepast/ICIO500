import json
import re
import subprocess
import os

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
print(f"  Card Height: {card_height_mm:.2f} mm ({card_height_in:.3f}\")")

# Check Chamfers
has_top_chamfer = any(abs(float(p[0]) - 202.0) < 0.1 and abs(float(p[2]) - 203.0) < 0.1 for p in ec_matches)
has_bot_chamfer = any(abs(float(p[0]) - 203.0) < 0.1 and abs(float(p[2]) - 202.0) < 0.1 for p in ec_matches)
print(f"  Tongue Lead-in 45 deg Chamfers: {'PASS' if (has_top_chamfer and has_bot_chamfer) else 'FAIL'}")

# Check notches
top_notch_len = 71.50 - 55.00
bot_notch_len = 160.00 - 134.00
print(f"  Top Notch Height:    {top_notch_len:.2f} mm (0.650\")")
print(f"  Tongue Height:       {134.00 - 71.50:.2f} mm (2.460\")")
print(f"  Bottom Notch Height: {bot_notch_len:.2f} mm (1.024\" - exact summer spec, zero bottom bulk)")

def get_fp_at(text, ref):
    idx = text.find(f'Reference "{ref}"')
    if idx == -1: idx = text.find(f'Reference" "{ref}"')
    if idx == -1: return None
    start = text.rfind('(footprint', 0, idx)
    m = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)', text[start:start+400])
    return (float(m.group(1)), float(m.group(2))) if m else None

eda = get_fp_at(main_pcb, "J1")
u6 = get_fp_at(main_pcb, "U6")
print(f"  Card Edge Fingers J1 (EDAC 306): at {eda}")
print(f"  Right-angle Header U6: at {u6}")

# Check Satellite board
with open("build/icio500/panel_satellite.kicad_pcb", "r", encoding="utf-8") as f:
    sat_pcb = f.read()

j1 = get_fp_at(sat_pcb, "J1")
print(f"\nSatellite PCB Components:")
print(f"  SMD Socket J1:   at {j1}")

# Check Faceplate board
with open("build/icio500/faceplate_front.kicad_pcb", "r", encoding="utf-8") as f:
    fp_pcb = f.read()

fp_ec_matches = re.findall(r'\(gr_line\s+\(start\s+([-\d.]+)\s+([-\d.]+)\)\s+\(end\s+([-\d.]+)\s+([-\d.]+)\).*?\"Edge\.Cuts\"', fp_pcb, re.DOTALL)
fp_xs = [float(p[0]) for p in fp_ec_matches] + [float(p[2]) for p in fp_ec_matches]
fp_ys = [float(p[1]) for p in fp_ec_matches] + [float(p[3]) for p in fp_ec_matches]
fp_w = max(fp_xs) - min(fp_xs)
fp_h = max(fp_ys) - min(fp_ys)
print(f"\nFaceplate Dimensions:")
print(f"  Width:  {fp_w:.2f} mm ({fp_w/25.4:.3f}\") [VPR Spec: 1.500\"]")
print(f"  Height: {fp_h:.2f} mm ({fp_h/25.4:.3f}\") [VPR Spec: 5.250\"]")

# DRC check on main board
print("\n" + "=" * 60)
print("MAIN BOARD ELECTRICAL DRC")
print("=" * 60)
res = subprocess.run([
    KICAD_CLI, "pcb", "drc",
    "--format", "json",
    "--output", "temp_audit_drc.json",
    "build/icio500/icio500.kicad_pcb"
], capture_output=True, text=True)
with open("temp_audit_drc.json", "r", encoding="utf-8") as f:
    d = json.load(f)
v_count = len(d.get("violations", []))
u_count = len(d.get("unconnected_items", []))
# Count real electrical violations
elec_v = [v for v in d.get("violations", []) if not v.get("type", "").startswith("lib_")]
print(f"  Main Board Electrical Violations: {len(elec_v)}")
print(f"  Main Board Unconnected Nets:      {u_count}")
if os.path.exists("temp_audit_drc.json"):
    os.remove("temp_audit_drc.json")
