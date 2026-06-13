import skip
import sys
import re

def parse_erc(report_file):
    with open(report_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    coords = set()
    matches = re.finditer(r'@\(([\d\.]+) mm, ([\d\.]+) mm\).*?\n\[unconnected_wire_endpoint\]', content, re.MULTILINE)
    for m in matches:
        x, y = float(m.group(1)), float(m.group(2))
        coords.add((x, y))
    return list(coords)

def trace_wires(schem_path, coords):
    sch = skip.Schematic(schem_path)
    print("Loaded schematic with skip.")
    
    # Create a map of wire endpoints
    wire_connections = {}
    for w in sch.wire:
        start = tuple(w.start.value)
        end = tuple(w.end.value)
        
        if start not in wire_connections:
            wire_connections[start] = []
        wire_connections[start].append(end)
        
        if end not in wire_connections:
            wire_connections[end] = []
        wire_connections[end].append(start)
        
    # Get all pins
    # skip doesn't easily expose symbol pins yet, it seems.
    # Wait, does sym.pin exist?
    
    pins = {}
    for sym in sch.symbol:
        ref = None
        for p in sym.property:
            if p.key == "Reference":
                ref = p.value
        
        # Where are the pins?
        # Let's just print attributes of a symbol
        print(f"Symbol {ref} at {sym.at.value}")
        # Actually skip doesn't resolve pin absolute coordinates easily.
    
    return

if __name__ == '__main__':
    coords = parse_erc('build/icio500/erc_report.txt')
    trace_wires('build/icio500/generated_schematic.kicad_sch', coords)
