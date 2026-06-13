import sys
import os

def create_lib():
    # Load our draw_opamps code to get the symbols
    sys.path.append(os.path.join(os.getcwd(), 'scratch'))
    import draw_opamps
    
    # We need to strip the (property "Footprint" ...) etc from the symbol string
    # wait, the symbol string in get_that1200_symbol() is:
    # (symbol "Amplifier_Audio:THAT1200" ... )
    # we need to replace "Amplifier_Audio:THAT1200" with "THAT1200"
    
    s1200 = draw_opamps.get_that1200_symbol().replace('"Amplifier_Audio:THAT1200"', '"THAT1200"')
    s1646 = draw_opamps.get_that1646_symbol().replace('"Amplifier_Audio:THAT1646"', '"THAT1646"')
    
    lib_content = f"""(kicad_symbol_lib (version 20211014) (generator kicad_symbol_editor)
{s1200}
{s1646}
)
"""
    with open("build/icio500/icio500.kicad_sym", "w", encoding='utf-8') as f:
        f.write(lib_content)
        
    # Also create sym-lib-table in build/icio500/
    table_content = """(sym_lib_table
  (lib (name "icio500")(type "KiCad")(uri "${KIPRJMOD}/icio500.kicad_sym")(options "")(descr ""))
)
"""
    with open("build/icio500/sym-lib-table", "w", encoding='utf-8') as f:
        f.write(table_content)
        
    print("Created library and sym-lib-table.")

if __name__ == '__main__':
    create_lib()
