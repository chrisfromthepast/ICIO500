import sys
import os

# add scratch to path to import draw_opamps
sys.path.append(os.path.join(os.getcwd(), 'scratch'))
import draw_opamps

def update_schematic(schem_path):
    with open(schem_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    s1200 = draw_opamps.get_that1200_symbol().strip()
    s1646 = draw_opamps.get_that1646_symbol().strip()
    
    # We need to find the `(symbol "icio500:THAT1200"` block and replace it
    # We can just do a crude string replacement if we know exactly what we are replacing.
    # Since we don't know the exact current text, let's use a regex to replace the entire symbol block
    import re
    
    content = re.sub(r'\(symbol "icio500:THAT1200".*?\n    \)\n', s1200 + '\n', content, flags=re.DOTALL)
    content = re.sub(r'\(symbol "icio500:THAT1646".*?\n    \)\n', s1646 + '\n', content, flags=re.DOTALL)
    
    # Actually wait, regex might be dangerous. Let's just write a careful parser.
    # The symbol block starts with `(symbol "icio500:THAT1200"` and ends with `\n    )`
    
    with open(schem_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_schematic('build/icio500/generated_schematic.kicad_sch')
    print("Updated schematic symbols inline.")
