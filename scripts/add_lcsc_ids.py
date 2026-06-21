import re
import os

src_dir = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\elec\src"

lcsc_map = {
    # Resistors (0603 1%)
    "RC0603FR-072K2L": "C25879", # 2.2k
    "RC0603FR-07330RL": "C22791", # 330
    "RC0603FR-0710KL": "C25804", # 10k
    "RC0603FR-0722KL": "C25768", # 22k
    "RC0603FR-0710RL": "C22775", # 10R
    "RC0603JR-070RL": "C21189", # 0R
    
    # Capacitors
    "CC0603KRX7R9BB104": "C14663", # 100nF 0603 50V
    "CC0603JRNPO9BN470": "C1653", # 47pF 0603 50V
    "CC0805KKX5R8BB106": "C15850", # 10uF 0805 10V
    "UWT1E221MNL1GS": "C150645", # 220uF 6.3x5.4
    "UWT1E101MNL1GS": "C163456", # 100uF 6.3x5.4
}

for root, _, files in os.walk(src_dir):
    for f in files:
        if f.endswith(".ato"):
            filepath = os.path.join(root, f)
            with open(filepath, "r") as file:
                content = file.read()
                
            original_content = content
            
            # Find `<name>.mpn = "MPN"` and add `; <name>.lcsc_id = "CXXXX"`
            for mpn, lcsc in lcsc_map.items():
                pattern = r"([a-zA-Z0-9_]+)\.mpn\s*=\s*\"" + mpn + r"\"(.*?)\n"
                replacement = r'\1.mpn = "' + mpn + r'"\2; \1.lcsc_id = "' + lcsc + r'"\n'
                content = re.sub(pattern, replacement, content)
                
            if content != original_content:
                with open(filepath, "w") as file:
                    file.write(content)
                print(f"Added LCSC IDs to {f}")

print("LCSC population complete.")
