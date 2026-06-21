import re
import os

src_dir = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\elec\src"

for root, _, files in os.walk(src_dir):
    for f in files:
        if f.endswith(".ato"):
            filepath = os.path.join(root, f)
            with open(filepath, "r", encoding="utf-8") as file:
                lines = file.readlines()
                
            modified = False
            for i, line in enumerate(lines):
                # We need to find `# <Some Text>;` and fix it.
                # Actually, any `#` that is followed by `;` or properties on the same line needs to be stripped.
                # Let's just find `# Yageo ... ;` or `# Nichicon ... ;`
                if '#' in line and ';' in line[line.find('#'):]:
                    # Extract the comment
                    comment_idx = line.find('#')
                    semicolon_idx = line.find(';', comment_idx)
                    
                    if semicolon_idx != -1:
                        # This means there are statements after the comment!
                        # We should just remove the comment text.
                        # We find the part between `#` and `;` (or maybe there are multiple `;`).
                        # Best way: remove everything from `#` to the first `;` after it?
                        # No, `# Yageo 22k; r_out.lcsc = ...`
                        # Let's just use regex to remove `# [^;]+;`
                        new_line = re.sub(r'#\s*[^;]*;\s*', '; ', line)
                        lines[i] = new_line
                        modified = True

            if modified:
                with open(filepath, "w", encoding="utf-8") as file:
                    file.writelines(lines)
                print(f"Fixed comments in {f}")

print("Comment fix complete.")
