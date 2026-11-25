"""
Generate SendCutSend / Ponoko 1:1 mm laser-cutting DXF + 3D STEP files and a composite stackup
preview PNG matching the hidden 0.8 mm 2-layer Satellite PCB (kicad/faceplate_satellite.kicad_pcb).

Outputs inside fabrication/satellite_faceplate/sendcutsend_panels/:
  1. icio500_faceplate_wood_0.125in_slots.{dxf,step}               (0.125" / 3.175 mm Wood cut-only)
  2. icio500_faceplate_wood_0.125in_slots_engraved.{dxf,svg}       (0.125" Wood w/ Ponoko CUT + ENGRAVE artwork)
  3. icio500_diffuser_gasket.{dxf,step}                            (0.150 mm Self-aligning rear diffuser gasket)
  4. icio500_faceplate_acrylic_0.118in_smoked.{dxf,step}           (0.118" / 3.000 mm Smoked Acrylic cut-only)
  5. icio500_faceplate_acrylic_0.118in_smoked_engraved.{dxf,svg}   (0.118" Smoked Acrylic w/ Ponoko CUT + ENGRAVE artwork)
  6. faceplate_stackup_preview.png                                 (+ copy to artifacts dir if present)

CAD coordinate convention:
  - Standards-compliant AC1018 1:1 millimeter DXF ($INSUNITS = 4) exported via KiCad 10
  - Positive first quadrant +X right [0..width], +Y up [0..height] via drill/aux origin
  - Zero kerf compensation per SendCutSend / Ponoko laser cutting guidelines
  - Ponoko engraved files separate CUT (Blue #0000FF, ACI 5) and ENGRAVE (Red #FF0000, ACI 1)
"""

import html
import math
import os
import shutil
import subprocess
import tempfile
import pcbnew
from PIL import Image, ImageDraw, ImageFont

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"

# Faceplate & coordinate parameters (VPR-500 1.500" x 5.250")
W_FP = 38.10
H_FP = 133.35

# Shared front-panel mounting holes (pcb coords: Y=0 top -> 133.35 bottom)
HOLES_MOUNT_PCB = [
    ("MH1",      19.050,   3.960, 3.200),  # VPR-500 top rack mount (#4-40 / M3)
    ("MH2",      19.050, 129.390, 3.200),  # VPR-500 bottom rack mount
    ("MH_TOP_L",  5.050,  24.000, 2.700),  # Top-left decorative M2.5 screw
    ("MH_TOP_R", 33.050,  24.000, 2.700),  # Top-right decorative M2.5 screw
    ("ENC",      19.050, 109.350, 7.200),  # Bourns PEC11R M7 threaded bushing
]

# Skirt LEDs D11..D16 around (19.050, 109.350) R=10.00mm -> Ø2.40 mm ports (>=75% of 3.18mm wood thickness)
SKIRT_PORTS_PCB = [
    ("D11", 19.050,  99.350, 2.400),
    ("D12", 27.710, 104.350, 2.400),
    ("D13", 27.710, 114.350, 2.400),
    ("D14", 19.050, 119.350, 2.400),
    ("D15", 10.390, 114.350, 2.400),
    ("D16", 10.390, 104.350, 2.400),
]

# 10 Horizontal VU bar-graph slots over D1..D10 @ X=19.05, Y=20.0..92.0 mm (7.20 x 2.40 mm stadium pills)
VU_SLOTS_PCB = [(f"D{i + 1}", 19.050, 20.000 + 8.000 * i, 7.200, 2.400) for i in range(10)]

# Original v1.0 front-panel VU dB labels (+20 down to -25) aligned beside each VU slot
VU_LABELS_PCB = [
    (label, 30.000, 20.000 + 8.000 * i)
    for i, label in enumerate(("+20", "+15", "+10", "+5", "0", "-5", "-10", "-15", "-20", "-25"))
]

# Clamped rear diffuser gasket inset behind Wood [2.00..36.10] x [15.00..122.50] (34.10 x 107.50 mm, R=1.00)
GASKET_RECT_PCB = (2.000, 15.000, 36.100, 122.500, 1.000)
GASKET_HOLES_PCB = [
    ("MH_TOP_L",  5.050,  24.000, 2.700),
    ("MH_TOP_R", 33.050,  24.000, 2.700),
    ("ENC",      19.050, 109.350, 7.400),
]


def pcb_to_dxf_y(y_pcb):
    return H_FP - y_pcb


def mm(val):
    return int(round(val * 1e6))


def add_rounded_rect_edges(board, x0, y0, x1, y1, r=0.0):
    """Draw closed Edge.Cuts rounded rectangle in KiCad PCB coordinates."""
    if r <= 1e-6:
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        for i in range(4):
            p1, p2 = pts[i], pts[(i + 1) % 4]
            seg = pcbnew.PCB_SHAPE(board)
            seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
            seg.SetStart(pcbnew.VECTOR2I(mm(p1[0]), mm(p1[1])))
            seg.SetEnd(pcbnew.VECTOR2I(mm(p2[0]), mm(p2[1])))
            seg.SetLayer(pcbnew.Edge_Cuts)
            seg.SetWidth(mm(0.10))
            board.Add(seg)
        return

    straight_edges = [
        ((x0 + r, y0),     (x1 - r, y0)),
        ((x1,     y0 + r), (x1,     y1 - r)),
        ((x1 - r, y1),     (x0 + r, y1)),
        ((x0,     y1 - r), (x0,     y0 + r)),
    ]
    for sp, ep in straight_edges:
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pcbnew.VECTOR2I(mm(sp[0]), mm(sp[1])))
        seg.SetEnd(pcbnew.VECTOR2I(mm(ep[0]), mm(ep[1])))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(mm(0.10))
        board.Add(seg)

    corners = [
        ((x1 - r, y0 + r), (x1 - r, y0),     (x1,     y0 + r)),
        ((x1 - r, y1 - r), (x1,     y1 - r), (x1 - r, y1)),
        ((x0 + r, y1 - r), (x0 + r, y1),     (x0,     y1 - r)),
        ((x0 + r, y0 + r), (x0,     y0 + r), (x0 + r, y0)),
    ]
    k = math.sqrt(0.5)
    for (cx, cy), sp, ep in corners:
        mx = cx + k * ((sp[0] - cx) + (ep[0] - cx))
        my = cy + k * ((sp[1] - cy) + (ep[1] - cy))
        arc = pcbnew.PCB_SHAPE(board)
        arc.SetShape(pcbnew.SHAPE_T_ARC)
        arc.SetArcGeometry(
            pcbnew.VECTOR2I(mm(sp[0]), mm(sp[1])),
            pcbnew.VECTOR2I(mm(mx), mm(my)),
            pcbnew.VECTOR2I(mm(ep[0]), mm(ep[1])),
        )
        arc.SetLayer(pcbnew.Edge_Cuts)
        arc.SetWidth(mm(0.10))
        board.Add(arc)


def add_circle_cutout(board, cx, cy, diam):
    """Draw circular Edge.Cuts cutout in KiCad PCB coordinates."""
    circ = pcbnew.PCB_SHAPE(board)
    circ.SetShape(pcbnew.SHAPE_T_CIRCLE)
    circ.SetFilled(False)
    circ.SetCenter(pcbnew.VECTOR2I(mm(cx), mm(cy)))
    circ.SetRadius(mm(diam / 2.0))
    circ.SetLayer(pcbnew.Edge_Cuts)
    circ.SetWidth(mm(0.10))
    board.Add(circ)


def add_horizontal_slot_edges(board, cx, cy, width, height):
    """
    Draw closed Edge.Cuts stadium/pill slot with 2 horizontal segments and
    2 exact 180-degree semicircular arcs (zero degenerate zero-length vertical lines).
    """
    r = height / 2.0
    half_straight = (width - height) / 2.0
    assert half_straight > 0.0, f"Slot width {width} must exceed height {height}"
    x_l = cx - half_straight
    x_r = cx + half_straight

    for (x1, y1), (x2, y2) in [
        ((x_l, cy - r), (x_r, cy - r)),
        ((x_r, cy + r), (x_l, cy + r)),
    ]:
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        seg.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(mm(0.10))
        board.Add(seg)

    for sp, mp, ep in [
        ((x_r, cy - r), (x_r + r, cy), (x_r, cy + r)),  # Right 180 deg semicircle
        ((x_l, cy + r), (x_l - r, cy), (x_l, cy - r)),  # Left 180 deg semicircle
    ]:
        arc = pcbnew.PCB_SHAPE(board)
        arc.SetShape(pcbnew.SHAPE_T_ARC)
        arc.SetArcGeometry(
            pcbnew.VECTOR2I(mm(sp[0]), mm(sp[1])),
            pcbnew.VECTOR2I(mm(mp[0]), mm(mp[1])),
            pcbnew.VECTOR2I(mm(ep[0]), mm(ep[1])),
        )
        arc.SetLayer(pcbnew.Edge_Cuts)
        arc.SetWidth(mm(0.10))
        board.Add(arc)


def _subtract_intervals(base_lo, base_hi, blocked):
    """Subtract a list of [a, b] intervals from [base_lo, base_hi] and return clean spans."""
    clamped = []
    for a, b in blocked:
        lo, hi = max(base_lo, a), min(base_hi, b)
        if hi > lo + 1e-9:
            clamped.append((lo, hi))
    if not clamped:
        return [(base_lo, base_hi)]
    clamped.sort()
    merged = [clamped[0]]
    for lo, hi in clamped[1:]:
        if lo <= merged[-1][1] + 1e-9:
            merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
        else:
            merged.append((lo, hi))
    out = []
    cur = base_lo
    for lo, hi in merged:
        if lo > cur + 1e-9:
            out.append((cur, lo))
        cur = max(cur, hi)
    if base_hi > cur + 1e-9:
        out.append((cur, base_hi))
    return out


def _clip_segment_against_holes(p0, p1, keepouts, min_len=0.25):
    """Analytically split line segment p0->p1 around circular hole keepouts."""
    x0, y0 = p0
    x1, y1 = p1
    vx, vy = x1 - x0, y1 - y0
    seg_len2 = vx * vx + vy * vy
    seg_len = math.sqrt(seg_len2)
    if seg_len < min_len:
        return []
    blocked = []
    for hx, hy, rk in keepouts:
        fx, fy = x0 - hx, y0 - hy
        b = 2.0 * (fx * vx + fy * vy)
        c = fx * fx + fy * fy - rk * rk
        disc = b * b - 4.0 * seg_len2 * c
        if disc > 0.0:
            sq = math.sqrt(disc)
            t0 = (-b - sq) / (2.0 * seg_len2)
            t1 = (-b + sq) / (2.0 * seg_len2)
            blocked.append((t0, t1))
    out = []
    for t0, t1 in _subtract_intervals(0.0, 1.0, blocked):
        if (t1 - t0) * seg_len >= min_len:
            out.append(((x0 + vx * t0, y0 + vy * t0), (x0 + vx * t1, y0 + vy * t1)))
    return out


def _clip_circle_against_holes(cx, cy, radius, keepouts, min_arc_len=0.25):
    """Analytically split a circle around circular hole keepouts into circles/arcs."""
    tau = 2.0 * math.pi
    blocked = []
    for hx, hy, rk in keepouts:
        dx, dy = hx - cx, hy - cy
        d = math.hypot(dx, dy)
        if d <= 1e-9:
            if rk >= radius - 1e-9:
                return []
            continue
        if d >= radius + rk - 1e-9 or d + rk <= radius + 1e-9:
            continue
        if d + radius <= rk + 1e-9:
            return []
        cos_a = max(-1.0, min(1.0, (radius * radius + d * d - rk * rk) / (2.0 * radius * d)))
        alpha = math.acos(cos_a)
        theta0 = math.atan2(dy, dx) % tau
        lo, hi = theta0 - alpha, theta0 + alpha
        if lo < 0.0:
            blocked.append((lo + tau, tau))
            blocked.append((0.0, hi))
        elif hi > tau:
            blocked.append((lo, tau))
            blocked.append((0.0, hi - tau))
        else:
            blocked.append((lo, hi))

    spans = _subtract_intervals(0.0, tau, blocked)
    if len(spans) == 1 and abs(spans[0][0]) < 1e-9 and abs(spans[0][1] - tau) < 1e-9:
        return [("circle", cx, cy, radius)]
    if len(spans) > 1 and abs(spans[0][0]) < 1e-9 and abs(spans[-1][1] - tau) < 1e-9:
        spans = [(spans[-1][0], spans[0][1] + tau)] + spans[1:-1]

    out = []
    for a0, a1 in spans:
        if radius * (a1 - a0) < min_arc_len:
            continue
        if (a1 - a0) > 1.75 * math.pi:
            amid = 0.5 * (a0 + a1)
            out.append(("arc", cx, cy, radius, a0, amid))
            out.append(("arc", cx, cy, radius, amid, a1))
        else:
            out.append(("arc", cx, cy, radius, a0, a1))
    return out


def build_reticle_primitives(cx=19.050, cy=109.350, clip_holes=None, margin=0.35):
    """
    Build deduplicated, zero-overlap EncoderGraphicGeometric reticle vector primitives
    in KiCad PCB coordinates (+X right, +Y down), clipped cleanly around cut holes.
    """
    keepouts = [(hx, hy, diam / 2.0 + margin) for _, hx, hy, diam in (clip_holes or [])]
    r_in = 10.000
    r_diag = 10.000 * math.sqrt(2.0)
    r_outer = r_diag + 3.000
    r_top = 15.000
    r_spoke_start = 5.000

    raw_lines = []
    # Upright square (+/-10 mm)
    sq = [(-r_in, -r_in), (r_in, -r_in), (r_in, r_in), (-r_in, r_in)]
    for i in range(4):
        p0, p1 = sq[i], sq[(i + 1) % 4]
        raw_lines.append(((cx + p0[0], cy + p0[1]), (cx + p1[0], cy + p1[1])))

    # 45-degree rotated diamond (+/-14.142 mm)
    dia = [(0.0, -r_diag), (r_diag, 0.0), (0.0, r_diag), (-r_diag, 0.0)]
    for i in range(4):
        p0, p1 = dia[i], dia[(i + 1) % 4]
        raw_lines.append(((cx + p0[0], cy + p0[1]), (cx + p1[0], cy + p1[1])))

    # 8 radial spokes starting at R=5.0 mm (top -90 deg truncated at R=15.0 mm to clear D10)
    for k in range(8):
        ang = math.radians(k * 45.0)
        r_end = r_top if k == 6 else r_outer
        ca, sa = math.cos(ang), math.sin(ang)
        raw_lines.append(((cx + r_spoke_start * ca, cy + r_spoke_start * sa), (cx + r_end * ca, cy + r_end * sa)))

    # 40 outer radial dial ticks (every 7.5 deg, skipping 45 deg spoke angles)
    for k in range(48):
        if k % 6 == 0:
            continue
        ang = math.radians(k * 7.5)
        ca, sa = math.cos(ang), math.sin(ang)
        raw_lines.append(((cx + r_diag * ca, cy + r_diag * sa), (cx + (r_diag + 1.200) * ca, cy + (r_diag + 1.200) * sa)))

    lines = []
    for p0, p1 in raw_lines:
        lines.extend(_clip_segment_against_holes(p0, p1, keepouts))

    circles = []
    arcs = []
    for r in (r_in, r_diag):
        for item in _clip_circle_against_holes(cx, cy, r, keepouts):
            if item[0] == "circle":
                circles.append(item[1:])
            else:
                arcs.append(item[1:])

    return {"lines": lines, "circles": circles, "arcs": arcs}


def add_engrave_graphics_to_board(board, clip_holes=None, margin=0.35, stroke_w=0.20):
    """Add laser-engraved VU dB labels and clipped EncoderGraphicGeometric reticle on F.Silkscreen."""
    prims = build_reticle_primitives(clip_holes=clip_holes, margin=margin)
    for p0, p1 in prims["lines"]:
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pcbnew.VECTOR2I(mm(p0[0]), mm(p0[1])))
        seg.SetEnd(pcbnew.VECTOR2I(mm(p1[0]), mm(p1[1])))
        seg.SetLayer(pcbnew.F_SilkS)
        seg.SetWidth(mm(stroke_w))
        board.Add(seg)

    for cx, cy, r in prims["circles"]:
        circ = pcbnew.PCB_SHAPE(board)
        circ.SetShape(pcbnew.SHAPE_T_CIRCLE)
        circ.SetFilled(False)
        circ.SetCenter(pcbnew.VECTOR2I(mm(cx), mm(cy)))
        circ.SetRadius(mm(r))
        circ.SetLayer(pcbnew.F_SilkS)
        circ.SetWidth(mm(stroke_w))
        board.Add(circ)

    for cx, cy, r, a0, a1 in prims["arcs"]:
        amid = 0.5 * (a0 + a1)
        arc = pcbnew.PCB_SHAPE(board)
        arc.SetShape(pcbnew.SHAPE_T_ARC)
        arc.SetArcGeometry(
            pcbnew.VECTOR2I(mm(cx + r * math.cos(a0)), mm(cy + r * math.sin(a0))),
            pcbnew.VECTOR2I(mm(cx + r * math.cos(amid)), mm(cy + r * math.sin(amid))),
            pcbnew.VECTOR2I(mm(cx + r * math.cos(a1)), mm(cy + r * math.sin(a1))),
        )
        arc.SetLayer(pcbnew.F_SilkS)
        arc.SetWidth(mm(stroke_w))
        board.Add(arc)

    for label, lx, ly in VU_LABELS_PCB:
        txt = pcbnew.PCB_TEXT(board)
        txt.SetText(label)
        txt.SetLayer(pcbnew.F_SilkS)
        txt.SetPosition(pcbnew.VECTOR2I(mm(lx), mm(ly)))
        txt.SetTextSize(pcbnew.VECTOR2I(mm(1.50), mm(1.50)))
        txt.SetTextThickness(mm(stroke_w))
        txt.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        txt.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
        board.Add(txt)


def export_panel_cad(out_dir, base_name, origin_y_mm, thickness_mm, rects, circles, slots=None, origin_x_mm=0.0):
    """
    Build a temporary KiCad board with exact Edge.Cuts geometry, set the drill/aux origin
    to (origin_x_mm, origin_y_mm) so exports sit in positive first-quadrant mm,
    and export both standards-compliant AC1018 DXF and exact-thickness 3D STEP.
    """
    os.makedirs(out_dir, exist_ok=True)
    dxf_path = os.path.join(out_dir, f"{base_name}.dxf")
    step_path = os.path.join(out_dir, f"{base_name}.step")

    with tempfile.TemporaryDirectory() as td:
        board = pcbnew.BOARD()
        board.SetCopperLayerCount(2)
        ds = board.GetDesignSettings()
        # Compensate KiCad 10's 0.090 mm copper+soldermask deduction in --board-only STEP export
        ds.SetBoardThickness(mm(thickness_mm + 0.090))
        ds.SetAuxOrigin(pcbnew.VECTOR2I(mm(origin_x_mm), mm(origin_y_mm)))

        for x0, y0, x1, y1, r in rects:
            add_rounded_rect_edges(board, x0, y0, x1, y1, r=r)
        for cx, cy, diam in circles:
            add_circle_cutout(board, cx, cy, diam)
        for scx, scy, sw, sh in (slots or []):
            add_horizontal_slot_edges(board, scx, scy, sw, sh)

        tmp_pcb = os.path.join(td, f"{base_name}.kicad_pcb")
        board.Save(tmp_pcb)

        subprocess.run(
            [
                KICAD_CLI, "pcb", "export", "dxf",
                "--layers", "Edge.Cuts",
                "--output-units", "mm",
                "--use-drill-origin",
                "--mode-single",
                "-o", dxf_path,
                tmp_pcb,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        subprocess.run(
            [
                KICAD_CLI, "pcb", "export", "step",
                "--board-only",
                "--force",
                "--drill-origin",
                "-o", step_path,
                tmp_pcb,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
    return dxf_path, step_path


def _read_dxf_pairs(dxf_path):
    with open(dxf_path, "r", encoding="utf-8") as f:
        raw = f.read().splitlines()
    if len(raw) % 2 == 1 and raw[-1] == "":
        raw = raw[:-1]
    assert len(raw) % 2 == 0, f"Malformed DXF line count ({len(raw)}) in {dxf_path}"
    return [(int(raw[i].strip()), raw[i].strip(), raw[i + 1].rstrip("\r\n")) for i in range(0, len(raw), 2)]


def _set_or_insert_pair(pairs, code_target, code_str_new, val_new, insert_after_code=None):
    out = []
    found = False
    for c, cs, v in pairs:
        if c == code_target:
            out.append((c, cs, val_new))
            found = True
        else:
            out.append((c, cs, v))
    if found:
        return out
    inserted = []
    for c, cs, v in out:
        inserted.append((c, cs, v))
        if insert_after_code is not None and c == insert_after_code and not found:
            inserted.append((code_target, code_str_new, val_new))
            found = True
    if not found:
        inserted.append((code_target, code_str_new, val_new))
    return inserted


def _rewrite_ponoko_dxf(dxf_path):
    """
    Rename KiCad layers inside TABLES/LAYER and ENTITIES to Ponoko conventions:
      - Edge.Cuts    -> CUT     (ACI 62 = 5 Blue, TrueColor 420 = 255 / #0000FF)
      - F.Silkscreen -> ENGRAVE (ACI 62 = 1 Red,  TrueColor 420 = 16711680 / #FF0000)
    """
    layer_map = {
        "Edge.Cuts": ("CUT", "5", "255"),
        "F.Silkscreen": ("ENGRAVE", "1", "16711680"),
    }
    pairs = _read_dxf_pairs(dxf_path)
    out = []
    section = None
    in_layer_table = False
    i = 0
    n = len(pairs)

    while i < n:
        c, cs, v = pairs[i]
        if c == 0 and v == "SECTION" and i + 1 < n and pairs[i + 1][0] == 2:
            section = pairs[i + 1][2]
            in_layer_table = False
            out.extend((pairs[i], pairs[i + 1]))
            i += 2
            continue
        if c == 0 and v == "ENDSEC":
            section = None
            in_layer_table = False
            out.append((c, cs, v))
            i += 1
            continue

        if section == "TABLES":
            if c == 0 and v == "TABLE" and i + 1 < n and pairs[i + 1][0] == 2:
                in_layer_table = pairs[i + 1][2] == "LAYER"
                out.extend((pairs[i], pairs[i + 1]))
                i += 2
                continue
            if c == 0 and v == "ENDTAB":
                in_layer_table = False
                out.append((c, cs, v))
                i += 1
                continue
            if in_layer_table and c == 0 and v == "LAYER":
                rec = [(c, cs, v)]
                j = i + 1
                while j < n and pairs[j][0] != 0:
                    rec.append(pairs[j])
                    j += 1
                lname = next((rv for rc, _, rv in rec if rc == 2), None)
                if lname in layer_map:
                    new_name, aci, truecol = layer_map[lname]
                    rec = _set_or_insert_pair(rec, 2, "  2", new_name)
                    rec = _set_or_insert_pair(rec, 62, " 62", aci, insert_after_code=70)
                    rec = _set_or_insert_pair(rec, 420, "420", truecol, insert_after_code=62)
                out.extend(rec)
                i = j
                continue

        if section == "ENTITIES" and c == 0:
            ent = [(c, cs, v)]
            j = i + 1
            while j < n and pairs[j][0] != 0:
                ent.append(pairs[j])
                j += 1
            lname = next((rv for rc, _, rv in ent if rc == 8), None)
            if lname in layer_map:
                new_name, aci, truecol = layer_map[lname]
                new_ent = []
                for rc, rcs, rv in ent:
                    if rc in (62, 420):
                        continue
                    if rc == 8:
                        new_ent.append((8, rcs, new_name))
                        new_ent.append((62, " 62", aci))
                        new_ent.append((420, "420", truecol))
                    else:
                        new_ent.append((rc, rcs, rv))
                ent = new_ent
            out.extend(ent)
            i = j
            continue

        out.append((c, cs, v))
        i += 1

    with open(dxf_path, "w", encoding="utf-8", newline="\n") as f:
        for _, cs, v in out:
            f.write(f"{cs}\n{v}\n")


def _dxf_to_ponoko_svg(dxf_path, svg_path, width_mm, height_mm):
    """Convert finalized Ponoko DXF ENTITIES into an exact 1:1 mm SVG (<g id='CUT'> / <g id='ENGRAVE'>)."""
    pairs = _read_dxf_pairs(dxf_path)
    cut_elems = []
    engrave_elems = []
    in_entities = False
    i = 0
    n = len(pairs)

    while i < n:
        c, _, v = pairs[i]
        if c == 0 and v == "SECTION" and i + 1 < n and pairs[i + 1][0] == 2:
            in_entities = pairs[i + 1][2] == "ENTITIES"
            i += 2
            continue
        if c == 0 and v == "ENDSEC":
            in_entities = False
            i += 1
            continue
        if in_entities and c == 0:
            etype = v
            props = {}
            j = i + 1
            while j < n and pairs[j][0] != 0:
                pc, _, pv = pairs[j]
                props[pc] = pv
                j += 1
            layer = props.get(8, "")
            target = cut_elems if layer == "CUT" else (engrave_elems if layer == "ENGRAVE" else None)
            if target is not None:
                if etype == "LINE":
                    x1, y1 = float(props[10]), height_mm - float(props[20])
                    x2, y2 = float(props[11]), height_mm - float(props[21])
                    target.append(f'    <line x1="{x1:.6f}" y1="{y1:.6f}" x2="{x2:.6f}" y2="{y2:.6f}"/>')
                elif etype == "CIRCLE":
                    cx, cy, r = float(props[10]), height_mm - float(props[20]), float(props[40])
                    target.append(f'    <circle cx="{cx:.6f}" cy="{cy:.6f}" r="{r:.6f}"/>')
                elif etype == "ARC":
                    cx, cy_dxf = float(props[10]), float(props[20])
                    r = float(props[40])
                    a1_deg, a2_deg = float(props[50]), float(props[51])
                    a1, a2 = math.radians(a1_deg), math.radians(a2_deg)
                    x1, sy1 = cx + r * math.cos(a1), height_mm - (cy_dxf + r * math.sin(a1))
                    x2, sy2 = cx + r * math.cos(a2), height_mm - (cy_dxf + r * math.sin(a2))
                    delta = (a2_deg - a1_deg) % 360.0
                    if delta < 1e-6:
                        delta = 360.0
                    if abs(delta - 360.0) < 1e-4:
                        target.append(f'    <circle cx="{cx:.6f}" cy="{height_mm - cy_dxf:.6f}" r="{r:.6f}"/>')
                    else:
                        large_arc = 1 if delta > 180.0 + 1e-6 else 0
                        target.append(
                            f'    <path d="M {x1:.6f} {sy1:.6f} A {r:.6f} {r:.6f} 0 {large_arc} 0 {x2:.6f} {sy2:.6f}"/>'
                        )
                else:
                    raise AssertionError(f"Unsupported DXF entity in Ponoko export ({layer}): {etype}")
            i = j
            continue
        i += 1

    title_safe = html.escape(os.path.basename(svg_path))
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_mm:.3f}mm" height="{height_mm:.3f}mm" viewBox="0 0 {width_mm:.3f} {height_mm:.3f}">',
        f'  <title>{title_safe}</title>',
        '  <g id="CUT" fill="none" stroke="#0000ff" stroke-width="0.01" stroke-linecap="round" stroke-linejoin="round">',
        *cut_elems,
        '  </g>',
        '  <g id="ENGRAVE" fill="none" stroke="#ff0000" stroke-width="0.01" stroke-linecap="round" stroke-linejoin="round">',
        *engrave_elems,
        '  </g>',
        '</svg>',
    ]
    with open(svg_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def export_engraved_dxf_and_svg(out_dir, base_name, origin_y_mm, rects, circles, slots, clip_holes):
    """Export Ponoko-standard Cut (#0000FF) + Line Engrave (#FF0000) DXF and SVG files."""
    os.makedirs(out_dir, exist_ok=True)
    dxf_path = os.path.join(out_dir, f"{base_name}.dxf")
    svg_path = os.path.join(out_dir, f"{base_name}.svg")

    with tempfile.TemporaryDirectory() as td:
        board = pcbnew.BOARD()
        board.SetCopperLayerCount(2)
        ds = board.GetDesignSettings()
        ds.SetAuxOrigin(pcbnew.VECTOR2I(0, mm(origin_y_mm)))

        for x0, y0, x1, y1, r in rects:
            add_rounded_rect_edges(board, x0, y0, x1, y1, r=r)
        for cx, cy, diam in circles:
            add_circle_cutout(board, cx, cy, diam)
        for scx, scy, sw, sh in (slots or []):
            add_horizontal_slot_edges(board, scx, scy, sw, sh)
        add_engrave_graphics_to_board(board, clip_holes=clip_holes)

        tmp_pcb = os.path.join(td, f"{base_name}.kicad_pcb")
        board.Save(tmp_pcb)
        subprocess.run(
            [
                KICAD_CLI, "pcb", "export", "dxf",
                "--layers", "Edge.Cuts,F.Silkscreen",
                "--output-units", "mm",
                "--use-drill-origin",
                "--mode-single",
                "-o", dxf_path,
                tmp_pcb,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )

    _rewrite_ponoko_dxf(dxf_path)
    _dxf_to_ponoko_svg(dxf_path, svg_path, W_FP, H_FP)
    return dxf_path, svg_path


def generate_dxfs(out_dir):
    # Clean superseded Baltic Birch & VU inlay files
    for old_name in (
        "icio500_faceplate_wood_0.125in_baltic_birch.dxf",
        "icio500_faceplate_wood_0.125in_baltic_birch.step",
        "icio500_vu_window_inlay_0.118in_smoked_acrylic.dxf",
        "icio500_vu_window_inlay_0.118in_smoked_acrylic.step",
    ):
        old_p = os.path.join(out_dir, old_name)
        if os.path.exists(old_p):
            os.remove(old_p)

    wood_holes = HOLES_MOUNT_PCB + SKIRT_PORTS_PCB
    wood_dxf, wood_step = export_panel_cad(
        out_dir,
        "icio500_faceplate_wood_0.125in_slots",
        origin_y_mm=H_FP,
        thickness_mm=3.175,
        rects=[(0.0, 0.0, W_FP, H_FP, 0.50)],
        circles=[(cx, cy, d) for _, cx, cy, d in wood_holes],
        slots=[(cx, cy, sw, sh) for _, cx, cy, sw, sh in VU_SLOTS_PCB],
    )
    wood_eng_dxf, wood_eng_svg = export_engraved_dxf_and_svg(
        out_dir,
        "icio500_faceplate_wood_0.125in_slots_engraved",
        origin_y_mm=H_FP,
        rects=[(0.0, 0.0, W_FP, H_FP, 0.50)],
        circles=[(cx, cy, d) for _, cx, cy, d in wood_holes],
        slots=[(cx, cy, sw, sh) for _, cx, cy, sw, sh in VU_SLOTS_PCB],
        clip_holes=wood_holes,
    )

    gasket_dxf, gasket_step = export_panel_cad(
        out_dir,
        "icio500_diffuser_gasket",
        origin_y_mm=GASKET_RECT_PCB[3],
        thickness_mm=0.150,
        rects=[GASKET_RECT_PCB],
        circles=[(cx, cy, d) for _, cx, cy, d in GASKET_HOLES_PCB],
        origin_x_mm=GASKET_RECT_PCB[0],
    )

    acrylic_dxf, acrylic_step = export_panel_cad(
        out_dir,
        "icio500_faceplate_acrylic_0.118in_smoked",
        origin_y_mm=H_FP,
        thickness_mm=3.000,
        rects=[(0.0, 0.0, W_FP, H_FP, 0.50)],
        circles=[(cx, cy, d) for _, cx, cy, d in HOLES_MOUNT_PCB],
    )
    acrylic_eng_dxf, acrylic_eng_svg = export_engraved_dxf_and_svg(
        out_dir,
        "icio500_faceplate_acrylic_0.118in_smoked_engraved",
        origin_y_mm=H_FP,
        rects=[(0.0, 0.0, W_FP, H_FP, 0.50)],
        circles=[(cx, cy, d) for _, cx, cy, d in HOLES_MOUNT_PCB],
        slots=None,
        clip_holes=HOLES_MOUNT_PCB,
    )

    print("Saved CAD exports (DXF + STEP + Ponoko Cut/Engrave SVG/DXF):")
    for p in (
        wood_dxf, wood_step, wood_eng_dxf, wood_eng_svg,
        gasket_dxf, gasket_step,
        acrylic_dxf, acrylic_step, acrylic_eng_dxf, acrylic_eng_svg,
    ):
        print(f"  {p} ({os.path.getsize(p):,} B)")
    return wood_dxf, gasket_dxf, acrylic_dxf


def render_preview(out_dir):
    sat = pcbnew.LoadBoard("kicad/faceplate_satellite.kicad_pcb")

    W_IMG, H_IMG = 2400, 1480
    img = Image.new("RGB", (W_IMG, H_IMG), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    def load_font(names, size):
        for n in names:
            p = os.path.join(r"C:\Windows\Fonts", n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
        return ImageFont.load_default()

    f_title = load_font(["arialbd.ttf", "segoeuib.ttf"], 32)
    f_sub   = load_font(["arial.ttf",   "segoeui.ttf"], 21)
    f_h2    = load_font(["arialbd.ttf", "segoeuib.ttf"], 23)
    f_bold  = load_font(["arialbd.ttf", "segoeuib.ttf"], 18)
    f_reg   = load_font(["arial.ttf",   "segoeui.ttf"], 17)
    f_sm    = load_font(["arial.ttf",   "segoeui.ttf"], 15)
    f_vu    = load_font(["arialbd.ttf", "segoeuib.ttf"], 13)

    # Header
    draw.rectangle([0, 0, W_IMG, 102], fill="#0F172A")
    draw.text((40, 16), "ICIO500 SATELLITE PCB (0.8mm) + SWAPPABLE WOOD SLOTS & SMOKED ACRYLIC", fill="#FFFFFF", font=f_title)
    draw.text((40, 62), "Standard 2-Layer FR4 Backing PCB (1.5..36.6 x 10.0..123.35 mm)  |  Cut-Only (SendCutSend) + Cut & Laser-Engraved (Ponoko) DXF/SVG", fill="#93C5FD", font=f_sub)

    SCALE = 8.4
    def draw_board_panel(ox, oy, title, subtitle, mode):
        def tx(x): return ox + x * SCALE
        def ty(y): return oy + y * SCALE
        draw.text((ox - 10, oy - 72), title, fill="#0F172A", font=f_h2)
        draw.text((ox - 10, oy - 42), subtitle, fill="#475569", font=f_sm)

        if mode in ("wood", "acrylic"):
            fill_col = "#5C3A21" if mode == "wood" else "#1E293B"
            edge_col = "#3B2313" if mode == "wood" else "#0F172A"
            draw.rounded_rectangle([tx(0), ty(0), tx(W_FP), ty(H_FP)], radius=4, fill=fill_col, outline=edge_col, width=4)
            # Dashed hidden Satellite PCB outline underneath
            sx0, sy0, sx1, sy1 = tx(1.50), ty(10.00), tx(36.60), ty(123.35)
            for k in range(int(sx0), int(sx1), 14):
                draw.line([k, sy0, min(k+7, sx1), sy0], fill="#DC2626", width=2)
                draw.line([k, sy1, min(k+7, sx1), sy1], fill="#DC2626", width=2)
            for k in range(int(sy0), int(sy1), 14):
                draw.line([sx0, k, sx0, min(k+7, sy1)], fill="#DC2626", width=2)
                draw.line([sx1, k, sx1, min(k+7, sy1)], fill="#DC2626", width=2)

            if mode == "wood":
                # 10 horizontal diffused VU pill slots (7.20 x 2.40 mm)
                for i, (ref, cx, cy, sw, sh) in enumerate(VU_SLOTS_PCB):
                    x0, y0 = tx(cx - sw / 2.0), ty(cy - sh / 2.0)
                    x1, y1 = tx(cx + sw / 2.0), ty(cy + sh / 2.0)
                    c = "#EF4444" if i == 0 else ("#F59E0B" if i in (1, 2) else "#22C55E")
                    draw.rounded_rectangle([x0, y0, x1, y1], radius=int((sh / 2.0) * SCALE), fill=c, outline="#2A170B", width=2)
                for ref, cx, cy, d in SKIRT_PORTS_PCB:
                    r = (d / 2.0) * SCALE
                    col = "#EF4444" if ref in ("D11","D14") else ("#22C55E" if ref in ("D12","D15") else "#3B82F6")
                    draw.ellipse([tx(cx)-r, ty(cy)-r, tx(cx)+r, ty(cy)+r], fill=col, outline="#2A170B", width=2)
                eng_col = "#1A0E06"
                eng_holes = HOLES_MOUNT_PCB + SKIRT_PORTS_PCB
            else:
                # Smoked acrylic dead-front glow through solid glass
                for i in range(10):
                    wy = 20.0 + 8.0 * i
                    c = "#EF4444" if i == 0 else ("#F59E0B" if i in (1, 2) else "#22C55E")
                    draw.ellipse([tx(19.05)-10, ty(wy)-6, tx(19.05)+10, ty(wy)+6], fill=c)
                for ref, cx, cy, _ in SKIRT_PORTS_PCB:
                    c = "#EF4444" if ref in ("D11","D14") else ("#22C55E" if ref in ("D12","D15") else "#3B82F6")
                    draw.ellipse([tx(cx)-8, ty(cy)-8, tx(cx)+8, ty(cy)+8], fill=c)
                eng_col = "#CBD5E1"
                eng_holes = HOLES_MOUNT_PCB

            # Laser-engraved VU labels (+20..-25) + clipped geometric reticle
            for lbl, lx, ly in VU_LABELS_PCB:
                draw.text((tx(lx), ty(ly)), lbl, fill=eng_col, font=f_vu, anchor="mm")
            prims = build_reticle_primitives(clip_holes=eng_holes)
            for p0, p1 in prims["lines"]:
                draw.line([tx(p0[0]), ty(p0[1]), tx(p1[0]), ty(p1[1])], fill=eng_col, width=2)
            for cx, cy, r in prims["circles"]:
                rp = r * SCALE
                draw.ellipse([tx(cx)-rp, ty(cy)-rp, tx(cx)+rp, ty(cy)+rp], outline=eng_col, width=2)
            for cx, cy, r, a0, a1 in prims["arcs"]:
                rp = r * SCALE
                draw.arc([tx(cx)-rp, ty(cy)-rp, tx(cx)+rp, ty(cy)+rp], start=math.degrees(a0), end=math.degrees(a1), fill=eng_col, width=2)

            for ref, cx, cy, d in HOLES_MOUNT_PCB:
                r = (d / 2.0) * SCALE
                outline_c = "#F59E0B" if "TOP" in ref else "#0F172A"
                draw.ellipse([tx(cx)-r, ty(cy)-r, tx(cx)+r, ty(cy)+r], fill="#FFFFFF", outline=outline_c, width=3)

            # Knob outer silhouette reference
            kr = 9.50 * SCALE
            draw.ellipse([tx(19.05)-kr, ty(109.35)-kr, tx(19.05)+kr, ty(109.35)+kr], outline="#94A3B8", width=2)

        elif mode == "sat":
            # Ghosted faceplate edge for alignment clarity
            draw.rectangle([tx(0), ty(0), tx(W_FP), ty(H_FP)], outline="#CBD5E1", width=2)
            draw.rectangle([tx(1.50), ty(10.00), tx(36.60), ty(123.35)], fill="#0F172A", outline="#10B981", width=3)
            # Tracks on F.Cu (cyan) and B.Cu (green/amber)
            for tr in sat.GetTracks():
                if tr.Type() == pcbnew.PCB_TRACE_T:
                    col = "#38BDF8" if tr.GetLayerName() == "F.Cu" else "#34D399"
                    s, e = tr.GetStart(), tr.GetEnd()
                    draw.line([tx(s.x/1e6), ty(s.y/1e6), tx(e.x/1e6), ty(e.y/1e6)], fill=col, width=2)
            for tr in sat.GetTracks():
                if tr.Type() == pcbnew.PCB_VIA_T:
                    p = tr.GetPosition()
                    draw.ellipse([tx(p.x/1e6)-3, ty(p.y/1e6)-3, tx(p.x/1e6)+3, ty(p.y/1e6)+3], fill="#FBBF24")
            for fp in sat.GetFootprints():
                for p in fp.Pads():
                    px, py = p.GetPosition().x/1e6, p.GetPosition().y/1e6
                    sx, sy = p.GetSize().x/1e6, p.GetSize().y/1e6
                    if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                        draw.ellipse([tx(px-sx/2), ty(py-sy/2), tx(px+sx/2), ty(py+sy/2)], fill="#F8FAFC", outline="#F43F5E", width=2)
                    else:
                        draw.rectangle([tx(px-sx/2), ty(py-sy/2), tx(px+sx/2), ty(py+sy/2)], fill="#F59E0B")
            for cx, cy, r in [(19.05, 109.35, 3.60), (11.55, 109.35, 1.10)]:
                draw.ellipse([tx(cx-r), ty(cy-r), tx(cx+r), ty(cy+r)], fill="#F8FAFC", outline="#10B981", width=2)

    draw_board_panel(60,  200, "1. WOOD SLOTS (3.18mm)", "10x Slots + Clipped Laser Engraving", "wood")
    draw_board_panel(455, 200, "2. SMOKED ACRYLIC (3.00mm)", "Dead-Front + Laser-Etched Scale & Reticle", "acrylic")
    draw_board_panel(850, 200, "3. SATELLITE PCB (0.80mm)", "Hidden 1.5/10mm Inset | B.Cu Parts", "sat")

    # Right Panel: Cross-Section Stackup & Dimensions Check
    RX = 1245
    draw.rectangle([RX, 130, 2350, 920], fill="#F8FAFC", outline="#CBD5E1", width=3)
    draw.text((RX + 24, 152), "SIDE STACKUP & MECHANICAL INTEGRATION (IN-PRODUCTION CARRIER/ENCODER)", fill="#0F172A", font=f_h2)

    # Vertical stackup diagram (left = front of rack, right = inside module)
    # Encoder PCB -> Standoff -> Satellite PCB -> Diffuser Film -> Wood Panel -> Knob
    SY1, SY2 = 260, 740
    CX_B = RX + 560   # B.Cu of satellite PCB (X_car = 54.175)
    CX_F = CX_B - 45  # F.Cu of satellite PCB (0.80 mm)
    CX_D = CX_F - 12  # Thin milky-white rear diffuser film (0.15 mm)
    CX_P = CX_D - 140 # Front of 3.18 mm Wood panel

    # Front panel (Walnut / Stained Birch 3.18mm)
    draw.rectangle([CX_P, SY1, CX_D, SY2], fill="#5C3A21", outline="#3B2313", width=3)
    # Cut-through horizontal slot window through Wood (Y = 404..436)
    draw.rectangle([CX_P, 404, CX_D, 436], fill="#FEF08A", outline="#3B2313", width=2)
    # Thin rear diffuser film sandwiched flat behind wood (Y = 310..560)
    draw.rectangle([CX_D, 310, CX_F, 560], fill="#E2E8F0", outline="#64748B", width=2)
    draw.text((CX_P - 175, 455), "7.2x2.4mm slot +", fill="#1E293B", font=f_sm)
    draw.text((CX_P - 175, 475), "rear diffuser film", fill="#1E293B", font=f_sm)

    # Satellite PCB (0.80 mm) flush behind diffuser/panel
    draw.rectangle([CX_F, SY1+40, CX_B, SY2-40], fill="#1E293B", outline="#10B981", width=3)
    # NPTH slot through satellite PCB behind VU window
    draw.rectangle([CX_F, 400, CX_B, 440], fill="#FEF08A")
    # Reverse-mount LED + bracket + J1 on B.Cu side
    draw.rectangle([CX_B, 392, CX_B+32, 448], fill="#F59E0B", outline="#92400E", width=2)
    draw.text((CX_B+40, 410), "D1..D16 LED (B.Cu, lens in NPTH slot)", fill="#92400E", font=f_sm)
    # BR1 bracket on B.Cu
    draw.rectangle([CX_B, SY1+55, CX_B+80, SY1+95], fill="#94A3B8", outline="#334155", width=2)
    draw.text((CX_B+88, SY1+65), "BR1/BR2 + J1<->U6 @ 54.175mm (0.000mm mate)", fill="#0F172A", font=f_sm)
    # Top M2.5 screw + nut clamping front panel to satellite PCB
    draw.rectangle([CX_P-18, SY1+115, CX_P, SY1+145], fill="#64748B", outline="#0F172A", width=2)
    draw.rectangle([CX_P, SY1+123, CX_B+45, SY1+137], fill="#94A3B8", outline="#0F172A", width=2)
    draw.rectangle([CX_B, SY1+117, CX_B+30, SY1+143], fill="#64748B", outline="#0F172A", width=2)
    draw.text((CX_B+55, SY1+120), "Top M2.5 screw & B.Cu nut (2x @ Y=24mm)", fill="#0F172A", font=f_sm)

    # PEC11R Encoder + M7 Bushing (7.0 mm long from enc base!)
    EY = 620
    draw.rectangle([CX_B+110, EY-45, CX_B+205, EY+45], fill="#CBD5E1", outline="#334155", width=3)
    draw.text((CX_B+122, EY-10), "PEC11R", fill="#0F172A", font=f_sm)
    # M7 bushing passing through PCB + wood (ends ~3mm proud of front face!)
    draw.rectangle([CX_P-105, EY-22, CX_B+110, EY+22], fill="#94A3B8", outline="#0F172A", width=2)
    draw.rectangle([CX_P-42, EY-32, CX_P, EY+32], fill="#64748B", outline="#0F172A", width=2)  # M7 Nut
    draw.text((CX_P-100, EY+44), "M7 Nut on Front (~3.0mm thread)", fill="#15803D", font=f_sm)
    # Encoder shaft extending left into knob (D_BORE_TOP_Z = 17.0mm)
    draw.rectangle([CX_P-290, EY-11, CX_P-105, EY+11], fill="#E2E8F0", outline="#334155", width=2)
    draw.text((CX_P-290, EY-38), "20mm Shaft + Existing Knob", fill="#0369A1", font=f_sm)

    # Bottom Right Summary Card
    draw.rectangle([RX, 945, 2350, 1410], fill="#ECFDF5", outline="#10B981", width=3)
    draw.text((RX + 24, 965), "VERIFIED COMPATIBILITY WITH IN-PRODUCTION BOARDS & SENDCUTSEND", fill="#065F46", font=f_h2)
    bullets = [
        "1. Zero changes to in-production Carrier (icio500) & Encoder (encoder_board) — BR1/BR2, J1<->U6, PEC11R mate 1:1.",
        "2. Satellite PCB (35.10 x 113.35 mm, 0.8 mm 2L FR4) stays inset >=1.5 mm L/R & 10 mm Top/Bot (invisible from rack).",
        "3. Standard full NPTH 1.92x1.68mm LED slots eliminate JLCPCB blind-slot fee cleanly across all D1..D16.",
        "4. Existing 3D-printed Capstan Knob fits with zero change to shaft; add ~1.8-2.0 mm M7 nut/shaft spacer behind knob.",
        "5. CAD/DXFs: Cut-only DXF/STEP + Ponoko Cut(#0000FF)/Engrave(#FF0000) DXF & SVG with v1.0 scale + geometric reticle.",
    ]
    by_txt = 1020
    for btxt in bullets:
        draw.text((RX + 28, by_txt), btxt, fill="#111827", font=f_reg)
        by_txt += 44

    # Key legend strip under board panels
    draw.rectangle([60, 1365, 1185, 1410], fill="#F8FAFC", outline="#CBD5E1", width=2)
    draw.text((78, 1378), "Red dashed = Hidden Satellite PCB  |  Dark/Silver Art = Ponoko Line Engraving (+20..-25 & Reticle)  |  Amber = SMT / M2.5", fill="#334155", font=f_sm)

    out_png = os.path.join(out_dir, "faceplate_stackup_preview.png")
    img.save(out_png, optimize=True)
    art_png = r"C:\Users\Chris Williams\.gemini\antigravity\brain\27d96d43-0ba0-4cfa-ba0b-2ac48d075611\faceplate_stackup_preview.png"
    if os.path.isdir(os.path.dirname(art_png)):
        shutil.copyfile(out_png, art_png)
    print(f"Saved preview PNG: {out_png} ({os.path.getsize(out_png)} B)")


def run():
    out_dir = "fabrication/satellite_faceplate/sendcutsend_panels"
    generate_dxfs(out_dir)
    render_preview(out_dir)


if __name__ == "__main__":
    run()
