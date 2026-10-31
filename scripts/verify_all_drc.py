import subprocess
import json
import os

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"

boards = [
    ("Carrier Card (icio500.kicad_pcb)", "build/icio500/icio500.kicad_pcb", "drc_carrier_card_final_verify.json"),
    ("Faceplate (faceplate_front.kicad_pcb)", "build/icio500/faceplate_front.kicad_pcb", "drc_faceplate_front_final_verify.json"),
    ("Satellite Board (panel_satellite.kicad_pcb)", "build/icio500/panel_satellite.kicad_pcb", "drc_panel_satellite_final_verify.json")
]

print("==================================================")
print("       FULL THREE-BOARD DRC VERIFICATION REPORT   ")
print("==================================================")

for title, path, rpt in boards:
    print(f"\n--- Checking {title} ---")
    cmd = [KICAD_CLI, "pcb", "drc", "--format", "json", "-o", rpt, path]
    subprocess.run(cmd, check=True)
    with open(rpt, 'r', encoding='utf-8') as f:
        d = json.load(f)
    violations = d.get('violations', [])
    unconn = d.get('unconnected_items', [])
    
    # Filter out lib_footprint_mismatch / lib_footprint_issues
    real_violations = [v for v in violations if v.get('type') not in ('lib_footprint_mismatch', 'lib_footprint_issues')]
    warnings = [v for v in violations if v.get('type') in ('lib_footprint_mismatch', 'lib_footprint_issues')]
    
    print(f"  Unconnected Items : {len(unconn)}")
    print(f"  Design Violations : {len(real_violations)}")
    print(f"  Library Warnings  : {len(warnings)}")
    
    if len(real_violations) > 0:
        for v in real_violations:
            print(f"    [ERROR] {v.get('type')}: {v.get('description')}")
    else:
        print("  -> ZERO ELECTRICAL/CLEARANCE DRC VIOLATIONS!")

print("\n==================================================")
