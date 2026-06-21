import re
import os

src_dir = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\elec\src"

for root, _, files in os.walk(src_dir):
    for f in files:
        if f.endswith(".ato"):
            filepath = os.path.join(root, f)
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()
                
            original_content = content
            
            # Find lines like `name = new Resistor; ...`
            # If they don't contain `.footprint =`, we inject one.
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '= new Resistor' in line and '.footprint' not in line:
                    # insert footprint
                    name = line.split('=')[0].strip()
                    lines[i] = line + f'; {name}.footprint = "Resistor_SMD:R_0603_1608Metric"'
                elif '= new Capacitor' in line and '.footprint' not in line:
                    # insert footprint
                    name = line.split('=')[0].strip()
                    lines[i] = line + f'; {name}.footprint = "Capacitor_SMD:C_0603_1608Metric"'
            
            new_content = '\n'.join(lines)
            if new_content != original_content:
                with open(filepath, "w", encoding="utf-8") as file:
                    file.write(new_content)
                print(f"Added footprints to {f}")

print("Footprints population complete.")
