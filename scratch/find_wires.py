import skip
import sys

def find_wire_endpoints(filepath):
    sch = skip.Schematic(filepath)
    
    endpoints = set()
    for w in sch.wire:
        endpoints.add(tuple(w.start.value))
        endpoints.add(tuple(w.end.value))
        
    u1_x = 90.17
    u1_y = 48.26
    
    print(f"Total wires found: {len(sch.wire)}")
    print("Wire endpoints near U1 (THAT1646) WITHOUT mirror applied:")
    for ex, ey in endpoints:
        if abs(ex - u1_x) < 20 and abs(ey - u1_y) < 20:
            rel_x = ex - u1_x
            rel_y = ey - u1_y
            print(f"Absolute: ({ex:6.2f}, {ey:6.2f})  --> Relative to U1: ({rel_x:6.2f}, {rel_y:6.2f})")

if __name__ == '__main__':
    find_wire_endpoints(sys.argv[1])
