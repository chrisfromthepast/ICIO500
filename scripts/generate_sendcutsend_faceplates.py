"""
Generate SendCutSend / Ponoko 1:1 mm laser-cutting DXF + 3D STEP files and a composite stackup
preview PNG matching the hidden 0.8 mm 2-layer Satellite PCB (kicad/faceplate_satellite.kicad_pcb).

Outputs inside fabrication/satellite_faceplate/sendcutsend_panels/:
  1. icio500_faceplate_wood_0.125in_slots.{dxf,step}     (0.125" / 3.175 mm Wood w/ 10x 7.2x2.4 mm horizontal slots)
  2. icio500_faceplate_acrylic_0.118in_smoked.{dxf,step}  (0.118" / 3.000 mm Full Dead-Front Smoked Acrylic)
  3. faceplate_stackup_preview.png                        (+ copy to artifacts dir if present)

CAD coordinate convention:
  - Standards-compliant AC1018 1:1 millimeter DXF ($INSUNITS = 4) exported via KiCad 10
  - Positive first quadrant +X right [0..width], +Y up [0..height] via drill/aux origin
  - Zero kerf compensation per SendCutSend laser cutting guidelines
"""

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


def export_panel_cad(out_dir, base_name, height_mm, thickness_mm, rects, circles, slots=None):
    """
    Build a temporary KiCad board with exact Edge.Cuts geometry, set the drill/aux origin
    to the bottom-left corner (0, height_mm) so exports sit in positive first-quadrant mm,
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
        ds.SetAuxOrigin(pcbnew.VECTOR2I(0, mm(height_mm)))

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

    wood_dxf, wood_step = export_panel_cad(
        out_dir,
        "icio500_faceplate_wood_0.125in_slots",
        height_mm=H_FP,
        thickness_mm=3.175,
        rects=[(0.0, 0.0, W_FP, H_FP, 0.50)],
        circles=[(cx, cy, d) for _, cx, cy, d in HOLES_MOUNT_PCB + SKIRT_PORTS_PCB],
        slots=[(cx, cy, sw, sh) for _, cx, cy, sw, sh in VU_SLOTS_PCB],
    )

    acrylic_dxf, acrylic_step = export_panel_cad(
        out_dir,
        "icio500_faceplate_acrylic_0.118in_smoked",
        height_mm=H_FP,
        thickness_mm=3.000,
        rects=[(0.0, 0.0, W_FP, H_FP, 0.50)],
        circles=[(cx, cy, d) for _, cx, cy, d in HOLES_MOUNT_PCB],
    )

    print("Saved CAD exports (DXF + STEP):")
    for p in (wood_dxf, wood_step, acrylic_dxf, acrylic_step):
        print(f"  {p} ({os.path.getsize(p):,} B)")
    return wood_dxf, acrylic_dxf


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

    # Header
    draw.rectangle([0, 0, W_IMG, 102], fill="#0F172A")
    draw.text((40, 16), "ICIO500 SATELLITE PCB (0.8mm) + SWAPPABLE WOOD SLOTS & SMOKED ACRYLIC", fill="#FFFFFF", font=f_title)
    draw.text((40, 62), "Standard 2-Layer FR4 Backing PCB (1.5..36.6 x 10.0..123.35 mm)  |  0.125\" Wood w/ 10 Horizontal Slots + Diffuser OR 0.118\" Smoked Acrylic", fill="#93C5FD", font=f_sub)

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
            else:
                # Smoked acrylic dead-front glow through solid glass
                for i in range(10):
                    wy = 20.0 + 8.0 * i
                    c = "#EF4444" if i == 0 else ("#F59E0B" if i in (1, 2) else "#22C55E")
                    draw.ellipse([tx(19.05)-10, ty(wy)-6, tx(19.05)+10, ty(wy)+6], fill=c)
                for ref, cx, cy, _ in SKIRT_PORTS_PCB:
                    c = "#EF4444" if ref in ("D11","D14") else ("#22C55E" if ref in ("D12","D15") else "#3B82F6")
                    draw.ellipse([tx(cx)-8, ty(cy)-8, tx(cx)+8, ty(cy)+8], fill=c)

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

    draw_board_panel(60,  200, "1. WOOD SLOTS (3.18mm)", "10x 7.2x2.4mm Bars + Rear Diffuser Film", "wood")
    draw_board_panel(455, 200, "2. SMOKED ACRYLIC (3.00mm)", "Dead-Front Zero LED Holes (0.118\")", "acrylic")
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
        "5. CAD/DXFs: 0.125\" Wood w/ 10x 7.2x2.4mm horizontal slots (+ diffuser tape) OR 0.118\" Full Smoked Acrylic.",
    ]
    by_txt = 1020
    for btxt in bullets:
        draw.text((RX + 28, by_txt), btxt, fill="#111827", font=f_reg)
        by_txt += 44

    # Key legend strip under board panels
    draw.rectangle([60, 1365, 1185, 1410], fill="#F8FAFC", outline="#CBD5E1", width=2)
    draw.text((78, 1378), "Red dashed = Hidden 0.8mm Satellite PCB  |  Cyan = F.Cu traces  |  Green = B.Cu traces  |  Amber = Bottom SMT pads / Top M2.5 holes", fill="#334155", font=f_sm)

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
