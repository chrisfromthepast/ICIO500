"""
layout_pcb.py  —  ICIO500 placement pass (v2 — Professionalized)
=================================================================
Places components, draws silkscreen bounding boxes and labels.
No tracks, no zones.
"""

import pcbnew, os, math

def mm(v):
    return int(v * 1_000_000)

def move(board, ref, x, y, rot=0):
    for fp in board.GetFootprints():
        if str(fp.GetReference()) == ref:
            fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
            fp.SetOrientationDegrees(rot)
            return
    print(f"  WARNING: {ref} not found")

# ─────────────────────────────────────────────────────────
#  Functional Block Placement Functions
# ─────────────────────────────────────────────────────────

def place_that1200_stage(board, x, y):
    """THAT1200 balanced input receiver + RF filter + clamping diodes"""
    move(board, 'U2', x, y)
    # Bypass caps
    move(board, 'C7', x + 4.5, y - 5)    # V+
    move(board, 'C8', x - 4.5, y + 6)    # V-
    move(board, 'C14', x + 7, y)         # Cm/Sm sense
    # AC coupling caps
    move(board, 'C12', x - 13, y - 3)
    move(board, 'C13', x - 13, y + 3)
    # RF filter (flowing left to right)
    move(board, 'R1',  x - 18, y - 3)
    move(board, 'C10', x - 23, y - 3)
    move(board, 'R2',  x - 18, y + 3)
    move(board, 'C11', x - 23, y + 3)
    move(board, 'C9',  x - 18, y, rot=90)
    # Input clamping diodes (in a neat column)
    move(board, 'D3', x - 8.5, y - 5)
    move(board, 'D4', x - 8.5, y - 2)
    move(board, 'D5', x - 8.5, y + 2)
    move(board, 'D6', x - 8.5, y + 5)

def place_that1646_stage(board, x, y):
    """THAT1646 balanced line driver + Zobel networks"""
    move(board, 'U4', x, y)
    # Bypass caps (Right side for V+, Left side for V-)
    move(board, 'C19', x + 8.5, y - 1)
    move(board, 'C20', x + 5.5, y - 1)
    move(board, 'C21', x - 8.5, y - 1)
    move(board, 'C22', x - 5.5, y - 1)
    # Ext caps (Top and Bottom)
    move(board, 'C23', x, y - 7)
    move(board, 'C24', x, y + 7)
    # Zobel network (Left side)
    move(board, 'R7',  x - 8.5, y - 4)
    move(board, 'C25', x - 13.0, y - 4)
    move(board, 'R8',  x - 8.5, y + 3)
    move(board, 'C26', x - 13.0, y + 3)

def place_level_shifter(board, x, y):
    """TL072 dual op-amp level scaling (attenuator + boost)"""
    move(board, 'U3', x, y)
    # Bypass caps
    move(board, 'C15', x + 4, y - 7)
    move(board, 'C16', x - 4, y + 7)
    # Half A (Left side)
    move(board, 'R3',  x - 7.5, y - 4)
    move(board, 'R4',  x - 7.5, y - 1)
    move(board, 'C17', x - 7.5, y + 2)
    # Half B (Right side)
    move(board, 'R5',  x + 7.5, y - 4)
    move(board, 'R6',  x + 7.5, y - 1)
    move(board, 'C18', x + 7.5, y + 2)

# ─────────────────────────────────────────────────────────
#  Silkscreen Drawing Helpers
# ─────────────────────────────────────────────────────────

def draw_bounding_box(board, x0, y0, x1, y1, line_w=0.15, corner_r=0.5):
    """Draw a rounded-corner rectangle on F.SilkS"""
    # Clamp corner radius
    w = abs(x1 - x0)
    h = abs(y1 - y0)
    r = min(corner_r, w / 4, h / 4)

    # Ensure x0 < x1, y0 < y1
    if x0 > x1: x0, x1 = x1, x0
    if y0 > y1: y0, y1 = y1, y0

    # Four straight edges (shortened by corner radius)
    edges = [
        # Top edge
        (x0 + r, y0, x1 - r, y0),
        # Bottom edge
        (x0 + r, y1, x1 - r, y1),
        # Left edge
        (x0, y0 + r, x0, y1 - r),
        # Right edge
        (x1, y0 + r, x1, y1 - r),
    ]
    for ex0, ey0, ex1, ey1 in edges:
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(mm(ex0), mm(ey0)))
        s.SetEnd(pcbnew.VECTOR2I(mm(ex1), mm(ey1)))
        s.SetWidth(mm(line_w))
        s.SetLayer(pcbnew.F_SilkS)
        board.Add(s)

    # Four corner arcs (approximated with short line segments)
    corners = [
        (x0 + r, y0 + r, 180, 270),  # Top-left
        (x1 - r, y0 + r, 270, 360),  # Top-right
        (x0 + r, y1 - r, 90, 180),   # Bottom-left
        (x1 - r, y1 - r, 0, 90),     # Bottom-right
    ]
    n_segs = 8  # segments per corner arc
    for cx, cy, a_start, a_end in corners:
        for i in range(n_segs):
            t0 = a_start + (a_end - a_start) * i / n_segs
            t1 = a_start + (a_end - a_start) * (i + 1) / n_segs
            px0 = cx + r * math.cos(math.radians(t0))
            py0 = cy - r * math.sin(math.radians(t0))
            px1 = cx + r * math.cos(math.radians(t1))
            py1 = cy - r * math.sin(math.radians(t1))
            s = pcbnew.PCB_SHAPE(board)
            s.SetShape(pcbnew.SHAPE_T_SEGMENT)
            s.SetStart(pcbnew.VECTOR2I(mm(px0), mm(py0)))
            s.SetEnd(pcbnew.VECTOR2I(mm(px1), mm(py1)))
            s.SetWidth(mm(line_w))
            s.SetLayer(pcbnew.F_SilkS)
            board.Add(s)

def draw_silkscreen_text(board, x, y, text, size=1.0, thickness=0.15):
    """Draw a text label on F.SilkS with consistent styling"""
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(thickness))
    board.Add(t)

def normalize_ref_designators(board, text_size=0.8, thickness=0.12):
    """Set all component reference designators to uniform size"""
    for fp in board.GetFootprints():
        ref = fp.Reference()
        ref.SetTextSize(pcbnew.VECTOR2I(mm(text_size), mm(text_size)))
        ref.SetTextThickness(mm(thickness))

# ─────────────────────────────────────────────────────────
#  Main Layout Function
# ─────────────────────────────────────────────────────────

def apply_layout():
    pcb_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "build", "icio500", "icio500.kicad_pcb"
    )
    board = pcbnew.LoadBoard(pcb_path)
    print("Board loaded.")

    has_u2 = any(str(fp.GetReference()) == 'U2' for fp in board.GetFootprints())
    if not has_u2:
        raise Exception("STOP! Run Update PCB from Schematic in KiCad first.")

    # ── Block Placement (Optimized for J1 pin proximity) ──────────
    #
    # J1 pin layout (Y coords):
    #   Pins 1-4 (Output):  Y = 75 – 87    → THAT1646 at Y=75
    #   Pins 7-10 (Input):  Y = 99 – 111   → THAT1200 at Y=105
    #   Pins 12-14 (Power): Y = 119 – 127  → PSU at Y=120
    #   TL072 scaling bridges to Daisy      → TL072 at Y=138
    #
    ANALOG_X = 165

    # Output stage — THAT1646 (top, near J1 output pins)
    place_that1646_stage(board, ANALOG_X, 70)

    # Level scaling — TL072 (middle, correctly bridges Output and Input)
    place_level_shifter(board, ANALOG_X, 90)

    # Input stage — THAT1200 (bottom, near J1 input pins)
    place_that1200_stage(board, ANALOG_X, 110)

    # ── Power Supply Group (tucked safely below analog column) ──────────
    PSU_X = 140
    PSU_Y = 130
    move(board, 'C1',  PSU_X + 5, PSU_Y - 4)    # V+ bulk electrolytic
    move(board, 'C3',  PSU_X + 5, PSU_Y + 4)    # V- bulk electrolytic
    move(board, 'C2',  PSU_X - 3, PSU_Y - 4)    # V+ ceramic
    move(board, 'C4',  PSU_X - 3, PSU_Y + 4)    # V- ceramic
    move(board, 'D1',  PSU_X - 9, PSU_Y - 4)    # V+ protection diode
    move(board, 'D2',  PSU_X - 9, PSU_Y + 4)    # V- protection diode

    # ── Daisy Seed & Digital Section (Tucked behind Analog Column) ───────
    DAISY_X = 100
    DAISY_Y = 105

    # Daisy Seed Socket
    move(board, 'U5', DAISY_X, DAISY_Y)

    # Isolated DCDC and its caps (Tucked top-left, near Daisy but clear of front)
    move(board, 'U1', 125, 70)
    move(board, 'C5', 129, 75)
    move(board, 'C6', 129, 81)

    # Switches and Headers (Moved safely inside the new cut line threshold X>65)
    move(board, 'U6', DAISY_X - 15, DAISY_Y + 15)
    move(board, 'J6', DAISY_X - 25, DAISY_Y + 15)
    move(board, 'U7', DAISY_X - 15, DAISY_Y + 35)
    move(board, 'J7', DAISY_X - 25, DAISY_Y + 35)

    # ── Clean old silkscreen drawings ─────────────────────────────
    for d in list(board.GetDrawings()):
        if d.GetLayer() == pcbnew.F_SilkS:
            board.Remove(d)

    # ── Board Title & Revision ────────────────────────────────────
    # Moved to the bottom safe zone so it doesn't get cut off!
    draw_silkscreen_text(board, 70, 160, "ICIO500", size=1.5, thickness=0.2)
    draw_silkscreen_text(board, 70, 163, "REV A", size=0.8, thickness=0.12)

    # ── Precision Silkscreen Bounding Boxes ─────────────────────────
    # Coordinates rigorously calculated from exact footprint bounding boxes + 0.5mm padding
    
    # OUTPUT STAGE box
    draw_bounding_box(board, 150.0, 60.4, 179.5, 78.3)
    draw_silkscreen_text(board, 164.75, 59.4, "OUTPUT STAGE")

    # LEVEL SCALING box
    draw_bounding_box(board, 155.5, 80.4, 178.4, 98.3)
    draw_silkscreen_text(board, 166.95, 79.4, "LEVEL SCALING")

    # INPUT STAGE box 
    draw_bounding_box(board, 140.2, 101.7, 179.5, 117.3)
    draw_silkscreen_text(board, 159.85, 100.7, "INPUT STAGE")

    # ANALOG PSU box
    draw_bounding_box(board, 127.0, 120.5, 150.3, 138.1)
    draw_silkscreen_text(board, 138.65, 119.5, "ANALOG PSU")

    # ISOLATED POWER box
    draw_bounding_box(board, 119.5, 61.8, 131.0, 88.2)
    draw_silkscreen_text(board, 125.25, 60.8, "ISOLATED POWER")

    # DAISY DIGITAL box
    draw_bounding_box(board, 82.7, 101.5, 117.3, 162.2)
    draw_silkscreen_text(board, 100.0, 100.5, "DAISY DIGITAL")

    print("Placement done. Blocks optimized. Bounding boxes drawn.")
    pcbnew.SaveBoard(pcb_path, board)

if __name__ == '__main__':
    apply_layout()
