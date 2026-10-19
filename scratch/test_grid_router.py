# Exact geometric router for U6 <-> U5
import sys

# We have a bounding box:
# X in [50, 120]
# Y in [80, 145]
# Grid spacing: 0.5 mm or 0.25 mm!
# Grid size: ~ 280 x 260 points.
# Two layers: F.Cu (0) and B.Cu (1).
# We want to route each net entirely on layer 0 OR layer 1 (NO VIAS!).
# And keep clearance >= 0.3mm to other traces and pads!

print("Testing exact grid router concept...")
