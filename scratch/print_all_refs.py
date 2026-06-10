from skip import Schematic
import os

sch_path = os.path.join("build", "icio500", "icio500.kicad_sch")
sch = Schematic(sch_path)

print("Symbols in schematic:")
for i, sym in enumerate(sch.symbol):
    ref_val = None
    val_val = None
    if hasattr(sym, 'property'):
        for prop in sym.property:
            if prop.name == 'Reference':
                ref_val = prop.value
            elif prop.name == 'Value':
                val_val = prop.value
    
    pos = sym.at if hasattr(sym, 'at') else 'Unknown'
    print(f"{i}: Ref={ref_val}, Value={val_val}, Pos={pos}")
