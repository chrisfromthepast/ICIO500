import sys
import uuid

def add_junctions(legacy_sch, kicad6_sch):
    with open(legacy_sch, 'r') as f:
        legacy_lines = f.readlines()
        
    junctions = []
    for line in legacy_lines:
        if line.startswith("Connection ~ "):
            coords = line.strip().split()[2:]
            x = float(coords[0]) * 0.0254
            y = float(coords[1]) * 0.0254
            junctions.append((x, y))
            
    if not junctions:
        print("No junctions found.")
        return
        
    with open(kicad6_sch, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # We will inject the junctions right before the (sheet_instances block
    idx = content.find('(sheet_instances')
    if idx == -1:
        print("Could not find insertion point!")
        return
        
    junction_str = ""
    for j in junctions:
        u = str(uuid.uuid4())
        junction_str += f"""  (junction (at {j[0]:.2f} {j[1]:.2f}) (diameter 0) (color 0 0 0 0)
    (uuid "{u}")
  )
"""
    
    new_content = content[:idx] + junction_str + content[idx:]
    
    with open(kicad6_sch, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Injected {len(junctions)} junctions.")

if __name__ == '__main__':
    add_junctions(sys.argv[1], sys.argv[2])
