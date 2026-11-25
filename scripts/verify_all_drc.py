import subprocess
import json
import os

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"

boards = [
    ("Carrier Card (icio500.kicad_pcb)", "kicad/icio500.kicad_pcb", "drc_carrier_card_final_verify.json"),
    ("Satellite PCB (faceplate_satellite.kicad_pcb)", "kicad/faceplate_satellite.kicad_pcb", "drc_faceplate_satellite_final_verify.json"),
    ("Encoder Daughtercard (encoder_board.kicad_pcb)", "kicad/encoder_board.kicad_pcb", "drc_encoder_board_final_verify.json")
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
    
    # Separate real errors from warnings
    errors = [v for v in violations if v.get('severity') == 'error' and v.get('type') not in ('lib_footprint_mismatch', 'lib_footprint_issues')]
    design_warnings = [v for v in violations if v.get('severity') == 'warning' and v.get('type') not in ('lib_footprint_mismatch', 'lib_footprint_issues')]
    lib_warnings = [v for v in violations if v.get('type') in ('lib_footprint_mismatch', 'lib_footprint_issues')]
    
    print(f"  Unconnected Items : {len(unconn)}")
    print(f"  Design Errors     : {len(errors)}")
    print(f"  Design Warnings   : {len(design_warnings)}")
    print(f"  Library Warnings  : {len(lib_warnings)}")
    
    if len(errors) > 0:
        for v in errors:
            print(f"    [ERROR] {v.get('type')}: {v.get('description')}")
    else:
        print("  -> ZERO ELECTRICAL/CLEARANCE DRC ERRORS!")

print("\n==================================================")
