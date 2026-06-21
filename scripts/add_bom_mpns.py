import re
import os

src_dir = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\elec\src"

rc_mpn_map = {
    # Resistors
    "2.2kohm": '"RC0603FR-072K2L" # Yageo 2.2k',
    "330ohm": '"RC0603FR-07330RL" # Yageo 330',
    "10kohm": '"RC0603FR-0710KL" # Yageo 10k',
    "22kohm": '"RC0603FR-0722KL" # Yageo 22k',
    "10ohm": '"RC0603FR-0710RL" # Yageo 10R',
    "0ohm": '"RC0603JR-070RL" # Yageo 0R',
    
    # Capacitors
    "100nF": '"CC0603KRX7R9BB104" # Yageo 100nF',
    "47pF": '"CC0603JRNPO9BN470" # Yageo 47pF',
    "10uF": '"CC0805KKX5R8BB106" # Yageo 10uF',
    "220uF": '"UWT1E221MNL1GS" # Nichicon 220uF',
    "100uF": '"UWT1E101MNL1GS" # Nichicon 100uF',
}

for root, _, files in os.walk(src_dir):
    for f in files:
        if f.endswith(".ato"):
            filepath = os.path.join(root, f)
            with open(filepath, "r") as file:
                content = file.read()
                
            original_content = content
            
            # Find all `var = new Resistor; var.value = X` and inject `var.mpn = ...`
            for val, mpn in rc_mpn_map.items():
                # regex to find `<name> = new Resistor; <name>.value = <val>`
                # and replace with `<name> = new Resistor; <name>.value = <val>; <name>.mpn = <mpn>`
                pattern = r"([a-zA-Z0-9_]+)\s*=\s*new (Resistor|Capacitor)\s*;\s*\1\.value\s*=\s*" + val
                replacement = r"\1 = new \2; \1.value = " + val + r"; \1.mpn = " + mpn
                content = re.sub(pattern, replacement, content)
                
            if content != original_content:
                with open(filepath, "w") as file:
                    file.write(content)
                print(f"Updated {f}")

print("BOM MPN population complete.")
