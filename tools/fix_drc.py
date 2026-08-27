"""
Fix DRC violations by rerouting problematic GND traces to B.Cu with vias.
"""
import re
import uuid

PCB_PATH = 'build/icio500/icio500.kicad_pcb'

def make_segment(sx, sy, ex, ey, net, width=0.4, layer="F.Cu"):
    uid = str(uuid.uuid4())
    return (
        f'\t(segment\n'
        f'\t\t(start {sx:.4f} {sy:.4f})\n'
        f'\t\t(end {ex:.4f} {ey:.4f})\n'
        f'\t\t(width {width})\n'
        f'\t\t(layer "{layer}")\n'
        f'\t\t(net "gnd")\n'
        f'\t\t(uuid "{uid}")\n'
        f'\t)\n'
    )

def make_via(x, y, net="gnd"):
    uid = str(uuid.uuid4())
    return (
        f'\t(via\n'
        f'\t\t(at {x:.4f} {y:.4f})\n'
        f'\t\t(size 0.6)\n'
        f'\t\t(drill 0.3)\n'
        f'\t\t(layers "F.Cu" "B.Cu")\n'
        f'\t\t(net "{net}")\n'
        f'\t\t(uuid "{uid}")\n'
        f'\t)\n'
    )

def main():
    with open(PCB_PATH, encoding='utf-8') as f:
        pcb = f.read()
    
    # === IDENTIFY AND REMOVE PROBLEMATIC SEGMENTS ===
    # These are the segments I added that cause shorts:
    
    # 1. U6 pin 3 GND -> existing GND: horizontal from ~95.91 to ~129.87
    #    This 33.96mm trace goes through all of U6's other pins
    # 2. U6 pin 5 GND -> U6 pin 3: short hop (this is fine, both are on same row, 
    #    but since pin 3's trace is bad, this chains into the problem)
    # 3. U6 pin 7 GND -> U6 pin 5: same issue
    # 4. J1 pin 13 GND -> existing: horizontal to 178.24, then vertical through D1/D2
    # 5. C20 pin 2 GND -> existing: crosses v_minus traces
    
    # Remove segments that match the problematic routes
    # Match by their exact coordinates from the autorouter output
    
    segments_to_remove = [
        # U6 pin 3 horizontal: (95.91, 107.00) -> (129.87, 107.00)
        (95.91, 107.0, 129.87, 107.0, "gnd"),
        # U6 pin 3 vertical: (129.87, 107.00) -> (129.87, 127.75) 
        (129.87, 107.0, 129.87, 127.75, "gnd"),
        # U6 pin 5 -> pin 3: (98.45, 107.00) -> (95.91, 107.00)
        (98.45, 107.0, 95.91, 107.0, "gnd"),
        # U6 pin 7 -> pin 5: (100.99, 107.00) -> (98.45, 107.00)
        (100.99, 107.0, 98.45, 107.0, "gnd"),
        # J1 pin 13 horizontal: (198.50, 122.66) -> (178.24, 122.66)
        (198.5, 122.66, 178.24, 122.66, "gnd"),
        # J1 pin 13 vertical: (178.24, 122.66) -> (178.24, 141.29)
        (178.24, 122.66, 178.24, 141.29, "gnd"),
        # C20 pin 2 horizontal: (155.24, 78.05) -> (156.53, 78.05)
        (155.24, 78.05, 156.53, 78.05, "gnd"),
        # C20 pin 2 vertical: (156.53, 78.05) -> (156.53, 77.06)
        (156.53, 78.05, 156.53, 77.06, "gnd"),
    ]
    
    removed_count = 0
    for sx, sy, ex, ey, net in segments_to_remove:
        # Build a pattern that matches the segment (with some tolerance in coordinates)
        # Look for the exact segment text
        pattern = (
            r'\t\(segment\n'
            r'\t\t\(start ' + f'{sx:.4f} {sy:.4f}' + r'\)\n'
            r'\t\t\(end ' + f'{ex:.4f} {ey:.4f}' + r'\)\n'
            r'\t\t\(width [\d.]+\)\n'
            r'\t\t\(layer "[^"]+"\)\n'
            r'\t\t\(net "' + net + r'"\)\n'
            r'\t\t\(uuid "[^"]+"\)\n'
            r'\t\)\n'
        )
        match = re.search(pattern, pcb)
        if match:
            pcb = pcb[:match.start()] + pcb[match.end():]
            removed_count += 1
            print(f"  Removed: ({sx}, {sy}) -> ({ex}, {ey}) [{net}]")
        else:
            print(f"  NOT FOUND: ({sx}, {sy}) -> ({ex}, {ey}) [{net}]")
    
    print(f"\nRemoved {removed_count} problematic segments")
    
    # === ADD CORRECTED ROUTING ===
    new_elements = []
    
    # --- FIX 1: U6 GND pins (3, 5, 7) ---
    # Route on B.Cu underneath the connector, then via up to GND network
    # U6 is at (93.37, 107.0) rotated 90deg
    # Pin 3 at abs (95.91, 107.00), Pin 5 at (98.45, 107.00), Pin 7 at (100.99, 107.00)
    # These are through-hole pads, so already connected on both layers
    
    # Connect pin 3, 5, 7 together on B.Cu (short hops between adjacent pins)
    new_elements.append(make_segment(95.91, 107.0, 98.45, 107.0, "gnd", 0.4, "B.Cu"))
    new_elements.append(make_segment(98.45, 107.0, 100.99, 107.0, "gnd", 0.4, "B.Cu"))
    
    # From pin 7, route on B.Cu to a clear area then via up to existing GND
    # Route south on B.Cu to avoid crossing signal pins, then east to GND network
    new_elements.append(make_segment(100.99, 107.0, 100.99, 112.0, "gnd", 0.4, "B.Cu"))
    new_elements.append(make_segment(100.99, 112.0, 129.87, 112.0, "gnd", 0.4, "B.Cu"))
    new_elements.append(make_segment(129.87, 112.0, 129.87, 127.75, "gnd", 0.4, "B.Cu"))
    # Via at the connection point to existing GND on F.Cu  
    new_elements.append(make_via(129.87, 127.75, "gnd"))
    print("  Added: U6 GND pins routed on B.Cu with via to GND network")
    
    # --- FIX 2: J1 pin 13 GND ---
    # Route on B.Cu to avoid crossing D1/D2 power diodes
    # J1 pin 13 at (198.50, 122.66) - this is a through-hole pad
    # Need to reach existing GND near (162.78, 141.29) area
    # Route on B.Cu south then west, avoiding the power section
    new_elements.append(make_segment(198.5, 122.66, 198.5, 145.0, "gnd", 0.4, "B.Cu"))
    new_elements.append(make_segment(198.5, 145.0, 162.78, 145.0, "gnd", 0.4, "B.Cu"))
    new_elements.append(make_segment(162.78, 145.0, 162.78, 141.29, "gnd", 0.4, "B.Cu"))
    new_elements.append(make_via(162.78, 141.29, "gnd"))
    print("  Added: J1 pin 13 GND routed on B.Cu via south side")
    
    # --- FIX 3: C20 pin 2 GND ---
    # Route on B.Cu to avoid crossing v_minus traces
    # C20 pin 2 at (155.24, 78.05) - SMD pad on F.Cu
    # Need a via first, then route on B.Cu to GND
    # Nearest GND is at (159.50, 78.0) area
    new_elements.append(make_via(155.24, 78.05, "gnd"))
    new_elements.append(make_segment(155.24, 78.05, 155.24, 80.5, "gnd", 0.4, "B.Cu"))
    new_elements.append(make_segment(155.24, 80.5, 159.50, 80.5, "gnd", 0.4, "B.Cu"))
    new_elements.append(make_segment(159.50, 80.5, 159.50, 78.0, "gnd", 0.4, "B.Cu"))
    new_elements.append(make_via(159.50, 78.0, "gnd"))
    print("  Added: C20 pin 2 GND routed on B.Cu with vias")
    
    # Insert new elements before final closing paren
    new_text = '\n'.join(new_elements)
    insert_pos = pcb.rfind('\n)')
    pcb = pcb[:insert_pos] + '\n' + new_text + pcb[insert_pos:]
    
    with open(PCB_PATH, 'w', encoding='utf-8') as f:
        f.write(pcb)
    
    print(f"\nWrote corrected PCB to {PCB_PATH}")

if __name__ == '__main__':
    main()
