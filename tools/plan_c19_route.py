"""Find C19 pad positions to route around them."""
import re

pcb = open('build/icio500/icio500.kicad_pcb', encoding='utf-8').read()

# Find C19 footprint block
c19_match = re.search(r'\(footprint [^\n]+\n(?:.*\n)*?.*"C19".*\n(?:.*\n)*?\t\)', pcb)

# Simpler: find pads near (159.5, 78) by scanning all segments touching the GND seg endpoint
# The DRC says C19 pad1 [v_plus] is at (160.46, 78.0) and pad2 [gnd] is at (159.5, 78.0)
# Let's confirm by finding the v_plus pad near (160.46, 78.0)

print("C19 geometry (from DRC report):")
print("  pad 1 [v_plus] at (160.46, 78.0)")
print("  pad 2 [gnd]    at (159.50, 78.0)")
print()

# The new GND segment from (159.5, 78.0) to (160.7, 79.2) passes 0.19mm from v_plus pad at (160.46, 78.0)
# v_plus pad radius ~ 0.75mm, gnd trace half-width 0.125mm, clearance 0.2mm
# Need segment to stay > 1.075mm from (160.46, 78.0)

# Better route: go LEFT from pad2 then down-left to the GND via at (157.5, 76.5)
# Or go south first then to GND via at (160.7, 79.2) via a jog below v_plus pad
# v_plus pad center (160.46, 78.0) - going below it at y=79.5 should be safe
# Route: (159.5, 78.0) -> (159.5, 79.5) -> (160.7, 79.5) -> (160.7, 79.2)

import math
vplus_x, vplus_y = 160.46, 78.0
# Check waypoints
for wx, wy in [(159.5, 79.5), (160.7, 79.5)]:
    d = math.sqrt((wx - vplus_x)**2 + (wy - vplus_y)**2)
    print(f"  waypoint ({wx},{wy}): dist to v_plus pad = {d:.3f}mm (need >1.075mm for 0.75+0.125+0.2)")

# Also check direct route south then east missing the pad
print()
# Route via (156.525, 77.055) GND via - going west then up
for wx, wy in [(157.5, 78.0), (157.5, 76.5)]:
    d = math.sqrt((wx - vplus_x)**2 + (wy - vplus_y)**2)
    print(f"  west-route ({wx},{wy}): dist to v_plus pad = {d:.3f}mm")
