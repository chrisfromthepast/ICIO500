import skip
import math
import sys

def snap_wires(schem_path, out_path):
    sch = skip.Schematic(schem_path)
    
    # Extract all absolute pin locations
    pins = []
    for sym in sch.symbol:
        # sym is an element_template.ElementTemplate or similar
        # wait, sym has 'at' which is [X, Y, angle]
        # and it has 'pin' collection?
        # But we don't know if skip exposes the pins from the library.
        pass
