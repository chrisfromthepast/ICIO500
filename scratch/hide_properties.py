import sys

def process(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    out = []
    in_prop = False
    prop_name = ""
    paren_depth = 0
    prop_depth = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Count depth change in this line
        depth_change = line.count('(') - line.count(')')
        
        if stripped.startswith('(property "'):
            parts = stripped.split('"')
            prop_name = parts[1] if len(parts) > 1 else ""
            in_prop = True
            prop_depth = paren_depth
            
        if in_prop and stripped.startswith('(effects'):
            if prop_name not in ["Reference", "Value"]:
                if "(hide yes)" not in line:
                    line = line.replace('(effects', '(effects (hide yes)')
        
        paren_depth += depth_change
        
        if in_prop and paren_depth <= prop_depth:
            in_prop = False
            
        out.append(line)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(out)

if __name__ == "__main__":
    process(sys.argv[1])
