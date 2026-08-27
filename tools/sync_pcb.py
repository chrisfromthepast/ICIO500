import re

def build_netlist(sch_path):
    with open(sch_path, 'r', encoding='utf-8') as f:
        sch_data = f.read()
    
    # 1. Parse symbol definitions to map UUIDs to References
    # format: (symbol (lib_id "...") (at ...) (unit 1) ... (uuid "...") (property "Reference" "J1" ...)
    symbols = {} # uuid -> ref
    for sym_match in re.finditer(r'\(symbol\s+[^)]*\s+\(uuid "([^"]+)"\).*?\(property "Reference" "([^"]+)"', sch_data, re.DOTALL):
        symbols[sym_match.group(1)] = sym_match.group(2)
        
    # Wait, the structure in KiCad 6+ is:
    # (symbol (lib_id ...) (at ...) (unit 1)
    #   (in_bom yes) (on_board yes) (dnp no)
    #   (uuid "...")
    #   (property "Reference" "J1" (uuid "...") ... )
    # Let's find all symbols:
    
    symbols = {}
    for block in re.finditer(r'\(symbol \(lib_id ".*?\n  \)', sch_data, re.DOTALL):
        block_text = block.group(0)
        uuid_match = re.search(r'\s\(uuid "([^"]+)"\)', block_text)
        ref_match = re.search(r'\(property "Reference" "([^"]+)"', block_text)
        if uuid_match and ref_match:
            symbols[uuid_match.group(1)] = ref_match.group(1)
            
    # 2. Parse connections (wires and labels) to find nets.
    # Actually, KiCad schematics don't store a pre-compiled netlist inside the .kicad_sch! They just store wires and pins.
    # It's better to just extract the netlist using KiCad Python API!
