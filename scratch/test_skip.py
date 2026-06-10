from skip import Schematic
import os

sch_path = os.path.join("build", "icio500", "icio500.kicad_sch")
sch = Schematic(sch_path)

print(f"Number of symbols: {len(sch.symbol)}")
for i, sym in enumerate(sch.symbol):
    print(f"Symbol {i}: {sym}")
    print(f"Attributes: {dir(sym)}")
    # Print properties if any
    if hasattr(sym, 'property'):
        print(f"Properties: {sym.property}")
        for prop in sym.property:
            print(f"  Prop: {dir(prop)} -> value: {getattr(prop, 'value', None)}, name: {getattr(prop, 'name', None)}")
    break
