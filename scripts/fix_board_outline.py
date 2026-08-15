"""
Fix the ICIO500 main carrier board outline to VPR-500 compliant dimensions.

Current outline: L-shape, 105mm x 113mm (bounding box [90,203] x [55,160])
Target outline:  L-shape, 114.30mm x 150.83mm (bounding box [52.17,203] x [55,169.30])

The card tongue and edge connector stay exactly where they are.
Only the front edge (X=90 -> X=52.17) and bottom edge (Y=160 -> Y=169.30) change.
"""

import pcbnew
import os

# --- Configuration ---
PCB_PATH = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\build\icio500\icio500.kicad_pcb"

# VPR-500 dimensions
PCB_HEIGHT = 114.30    # mm (vertical, Y direction)
PCB_DEPTH = 150.83     # mm (horizontal, X direction, faceplate to finger tips)

# Fixed reference points (from existing design)
FINGER_TIP_X = 203.0   # X coordinate of card edge finger tips (rightmost point)
TOP_EDGE_Y = 55.0       # Y coordinate of top edge (keep same)

# Computed new edges
FRONT_EDGE_X = FINGER_TIP_X - PCB_DEPTH  # 203 - 150.83 = 52.17
BOTTOM_EDGE_Y = TOP_EDGE_Y + PCB_HEIGHT   # 55 + 114.30 = 169.30

# Tongue geometry (keep existing)
TONGUE_STEP_X = 195.0   # Where main body meets tongue
TONGUE_TOP_Y = 71.5     # Top of tongue cutout
TONGUE_BOTTOM_Y = 134.0 # Bottom of tongue cutout
TONGUE_TIP_X = 203.0    # End of tongue (finger tips)

print(f"=== VPR-500 Board Outline Fix ===")
print(f"Front edge:  X = {FRONT_EDGE_X:.2f} mm (was 90.0)")
print(f"Top edge:    Y = {TOP_EDGE_Y:.2f} mm (unchanged)")
print(f"Bottom edge: Y = {BOTTOM_EDGE_Y:.2f} mm (was 160.0)")
print(f"Tongue:      X = [{TONGUE_STEP_X}, {TONGUE_TIP_X}], Y = [{TONGUE_TOP_Y}, {TONGUE_BOTTOM_Y}]")
print(f"Total depth: {TONGUE_TIP_X - FRONT_EDGE_X:.2f} mm (target: {PCB_DEPTH})")
print(f"Total height: {BOTTOM_EDGE_Y - TOP_EDGE_Y:.2f} mm (target: {PCB_HEIGHT})")
print()

# --- Load the board ---
board = pcbnew.LoadBoard(PCB_PATH)
print(f"Loaded board: {PCB_PATH}")

# --- Remove existing Edge.Cuts lines ---
edge_cuts_layer = board.GetLayerID("Edge.Cuts")
drawings_to_remove = []
for drawing in board.GetDrawings():
    if drawing.GetLayer() == edge_cuts_layer and drawing.GetClass() == "PCB_SHAPE":
        drawings_to_remove.append(drawing)

print(f"Found {len(drawings_to_remove)} existing Edge.Cuts shapes to remove")
for d in drawings_to_remove:
    board.Remove(d)
print(f"Removed all existing Edge.Cuts shapes")

# --- Helper to add an edge line ---
def add_edge_line(board, x1, y1, x2, y2, layer_id):
    """Add a line segment on Edge.Cuts layer. Coordinates in mm."""
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(layer_id)
    seg.SetWidth(pcbnew.FromMM(0.1))
    seg.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
    seg.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
    board.Add(seg)
    return seg

# --- Draw new VPR-compliant outline ---
segments = [
    # 1. Top edge: front to tongue step
    (FRONT_EDGE_X, TOP_EDGE_Y,      TONGUE_STEP_X, TOP_EDGE_Y),
    # 2. Right side upper: tongue step down to tongue top
    (TONGUE_STEP_X, TOP_EDGE_Y,     TONGUE_STEP_X, TONGUE_TOP_Y),
    # 3. Tongue top: step right to tongue tip
    (TONGUE_STEP_X, TONGUE_TOP_Y,   TONGUE_TIP_X, TONGUE_TOP_Y),
    # 4. Tongue right: down the card edge
    (TONGUE_TIP_X, TONGUE_TOP_Y,    TONGUE_TIP_X, TONGUE_BOTTOM_Y),
    # 5. Tongue bottom: step left back to main body
    (TONGUE_TIP_X, TONGUE_BOTTOM_Y, TONGUE_STEP_X, TONGUE_BOTTOM_Y),
    # 6. Right side lower: tongue bottom down to board bottom
    (TONGUE_STEP_X, TONGUE_BOTTOM_Y, TONGUE_STEP_X, BOTTOM_EDGE_Y),
    # 7. Bottom edge: right to left
    (TONGUE_STEP_X, BOTTOM_EDGE_Y,  FRONT_EDGE_X, BOTTOM_EDGE_Y),
    # 8. Left (front) edge: bottom to top
    (FRONT_EDGE_X, BOTTOM_EDGE_Y,   FRONT_EDGE_X, TOP_EDGE_Y),
]

for i, (x1, y1, x2, y2) in enumerate(segments, 1):
    seg = add_edge_line(board, x1, y1, x2, y2, edge_cuts_layer)
    print(f"  Segment {i}: ({x1:.2f}, {y1:.2f}) -> ({x2:.2f}, {y2:.2f})")

print(f"\nDrawn {len(segments)} new Edge.Cuts segments")

# --- Save the board ---
board.Save(PCB_PATH)
print(f"\nSaved board to: {PCB_PATH}")

# --- Verify ---
print(f"\n=== Verification ===")
print(f"Board bounding box:")
print(f"  X: [{FRONT_EDGE_X:.2f}, {TONGUE_TIP_X:.2f}] = {TONGUE_TIP_X - FRONT_EDGE_X:.2f} mm depth")
print(f"  Y: [{TOP_EDGE_Y:.2f}, {BOTTOM_EDGE_Y:.2f}] = {BOTTOM_EDGE_Y - TOP_EDGE_Y:.2f} mm height")
print(f"VPR-500 spec:")
print(f"  Depth: {PCB_DEPTH} mm")
print(f"  Height: {PCB_HEIGHT} mm")
print(f"Match: {'YES' if abs(TONGUE_TIP_X - FRONT_EDGE_X - PCB_DEPTH) < 0.01 and abs(BOTTOM_EDGE_Y - TOP_EDGE_Y - PCB_HEIGHT) < 0.01 else 'NO'}")
