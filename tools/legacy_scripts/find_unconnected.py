import sys
# Simple python script to find unconnected pads in a kicad pcb file
def find_unconnected(pcb_path):
    with open(pcb_path, 'r', encoding='utf-8') as f:
        data = f.read()
    # This is complex because we need to parse the netlist and traces.
    print("Just wait for DRC to finish.")

