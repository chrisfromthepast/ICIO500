"""
scripts/generate_carrier_rework_guide.py
----------------------------------------
Generates fabrication/in_production/jlcpcb_carrier/carrier_rev1_rework_visual_guide.png
directly from kicad/icio500.kicad_pcb without modifying any PCB, schematic, or fab files.

Produces a high-contrast 2800x2000 px workbench rework sheet covering:
  [Panel 1] Real F.Cu/F.SilkS carrier board locator map with exact coordinates
  [Panel 2] Pre-power fixes: C3 & C27 (180 deg flip) and D11 (BAT54S removal)
  [Panel 3] U2 (THAT1200S08-U) partial pin-lift rework (Pins 1-5 flat, 3 wires)
  [Panel 4] U4 (THAT1646S08-U / DIP-8 1646P08-U) belly-up dead-bug map (8 wires)
"""

import os
import subprocess
import tempfile
import pymupdf
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PCB_PATH = os.path.join(REPO_ROOT, "kicad", "icio500.kicad_pcb")
OUT_PNG = os.path.join(
    REPO_ROOT,
    "fabrication",
    "in_production",
    "jlcpcb_carrier",
    "carrier_rev1_rework_visual_guide.png",
)
KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"

CANVAS_W, CANVAS_H = 2800, 2000
PT_PER_MM = 72.0 / 25.4


def load_font(size: int, bold: bool = False, mono: bool = False):
    font_dir = r"C:\Windows\Fonts"
    if mono:
        candidates = ["consolab.ttf", "consola.ttf"] if bold else ["consola.ttf"]
    elif bold:
        candidates = ["segoeuib.ttf", "arialbd.ttf", "seguisb.ttf"]
    else:
        candidates = ["segoeui.ttf", "arial.ttf"]
    for fn in candidates:
        path = os.path.join(font_dir, fn)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


FONT_TITLE = load_font(34, bold=True)
FONT_SUBTITLE = load_font(20, bold=False)
FONT_WARN = load_font(23, bold=True)
FONT_PANEL_HDR = load_font(24, bold=True)
FONT_H3 = load_font(20, bold=True)
FONT_BODY = load_font(18, bold=False)
FONT_BODY_B = load_font(18, bold=True)
FONT_SMALL = load_font(15, bold=False)
FONT_SMALL_B = load_font(15, bold=True)
FONT_MONO = load_font(17, bold=False, mono=True)
FONT_MONO_B = load_font(17, bold=True, mono=True)
FONT_MONO_SM = load_font(15, bold=True, mono=True)
FONT_BADGE = load_font(19, bold=True)


def export_pcb_rasters():
    """Export 1:1 KiCad color PDF temporarily and rasterize exact crops."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, "carrier_top.pdf")
        subprocess.run(
            [
                KICAD_CLI,
                "pcb",
                "export",
                "pdf",
                "--layers",
                "F.Cu,F.SilkS,F.Mask,Edge.Cuts",
                "--mode-single",
                "--exclude-value",
                "--scale",
                "1",
                "--bg-color",
                "#14181F",
                "-o",
                pdf_path,
                PCB_PATH,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        doc = pymupdf.open(pdf_path)
        page = doc[0]

        # Overview crop covering carrier board Edge.Cuts X=[54.175, 203.0], Y=[45.7, 160.0]
        ov_mm = (52.0, 43.5, 205.0, 162.2)
        ov_clip = pymupdf.Rect(
            ov_mm[0] * PT_PER_MM,
            ov_mm[1] * PT_PER_MM,
            ov_mm[2] * PT_PER_MM,
            ov_mm[3] * PT_PER_MM,
        )
        ov_pix = page.get_pixmap(dpi=220, clip=ov_clip)
        ov_img = Image.frombytes("RGB", [ov_pix.width, ov_pix.height], ov_pix.samples)

        # Zoom crop 1: C3 region (X=159..185, Y=128..154)
        c3_mm = (159.0, 128.0, 185.0, 154.0)
        c3_clip = pymupdf.Rect(*(v * PT_PER_MM for v in c3_mm))
        c3_pix = page.get_pixmap(dpi=420, clip=c3_clip)
        c3_img = Image.frombytes("RGB", [c3_pix.width, c3_pix.height], c3_pix.samples)

        # Zoom crop 2: C27 + D11 region (X=139..163, Y=83..105)
        c27_mm = (139.0, 83.0, 163.0, 105.0)
        c27_clip = pymupdf.Rect(*(v * PT_PER_MM for v in c27_mm))
        c27_pix = page.get_pixmap(dpi=440, clip=c27_clip)
        c27_img = Image.frombytes("RGB", [c27_pix.width, c27_pix.height], c27_pix.samples)

        doc.close()
        return (ov_img, ov_mm), (c3_img, c3_mm), (c27_img, c27_mm)


def draw_round_rect(draw, box, radius, fill=None, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_panel_frame(draw, box, header_text, accent_color):
    x0, y0, x1, y1 = box
    draw_round_rect(draw, (x0, y0, x1, y1), 14, fill="#FFFFFF", outline="#CBD5E1", width=3)
    draw.rounded_rectangle((x0, y0, x1, y0 + 52), radius=14, fill="#0F172A")
    draw.rectangle((x0, y0 + 30, x1, y0 + 52), fill="#0F172A")
    draw.rectangle((x0, y0 + 50, x1, y0 + 54), fill=accent_color)
    draw.text((x0 + 20, y0 + 12), header_text, font=FONT_PANEL_HDR, fill="#F8FAFC")


def mm_to_px(wx, wy, mm_bounds, box_px):
    mx0, my0, mx1, my1 = mm_bounds
    px0, py0, px1, py1 = box_px
    x = px0 + (wx - mx0) / (mx1 - mx0) * (px1 - px0)
    y = py0 + (wy - my0) / (my1 - my0) * (py1 - py0)
    return int(round(x)), int(round(y))


def draw_badge(draw, cx, cy, label, bg="#DC2626", fg="#FFFFFF", w=34, h=30):
    x0, y0 = cx - w // 2, cy - h // 2
    draw_round_rect(draw, (x0, y0, x0 + w, y0 + h), 8, fill=bg, outline="#FFFFFF", width=2)
    bbox = draw.textbbox((0, 0), label, font=FONT_BADGE)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy - th // 2 - 2), label, font=FONT_BADGE, fill=fg)


def draw_cap_icon(draw, cx, cy, plus_on_left=True, wrong=False):
    """Draw physical aluminum electrolytic top-view diagram (chamfered + vs black stripe -)."""
    border_col = "#DC2626" if wrong else "#15803D"
    card_bg = "#FEF2F2" if wrong else "#F0FDF4"
    draw_round_rect(
        draw,
        (cx - 178, cy - 86, cx + 178, cy + 96),
        12,
        fill=card_bg,
        outline=border_col,
        width=3,
    )

    # SMD pads left & right
    draw.rectangle((cx - 94, cy - 22, cx - 50, cy + 18), fill="#C0C7D1", outline="#64748B", width=2)
    draw.rectangle((cx + 50, cy - 22, cx + 94, cy + 18), fill="#C0C7D1", outline="#64748B", width=2)

    # Base plastic carrier (chamfered on + side!)
    bx0, by0, bx1, by1 = cx - 64, cy - 58, cx + 64, cy + 54
    ch = 22
    if plus_on_left:
        poly = [
            (bx0 + ch, by0),
            (bx1, by0),
            (bx1, by1),
            (bx0 + ch, by1),
            (bx0, by1 - ch),
            (bx0, by0 + ch),
        ]
    else:
        poly = [
            (bx0, by0),
            (bx1 - ch, by0),
            (bx1, by0 + ch),
            (bx1, by1 - ch),
            (bx1 - ch, by1),
            (bx0, by1),
        ]
    draw.polygon(poly, fill="#1E293B", outline="#0F172A", width=2)

    # Metallic aluminum can
    cr = 44
    c_cy = cy - 2
    draw.ellipse((cx - cr, c_cy - cr, cx + cr, c_cy + cr), fill="#E2E8F0", outline="#64748B", width=3)

    # Cathode black D-band on '-' side (opposite chamfered '+' side!)
    if plus_on_left:
        draw.chord((cx - cr, c_cy - cr, cx + cr, c_cy + cr), start=-55, end=55, fill="#111827")
        draw.text((cx + 15, c_cy - 14), "-", font=FONT_PANEL_HDR, fill="#FFFFFF")
        draw.text((cx - 29, c_cy - 14), "+", font=FONT_PANEL_HDR, fill="#0F172A")
        draw.text((cx - 164, cy - 30), "v_minus\n(-16V)", font=FONT_SMALL_B, fill="#B91C1C")
        draw.text((cx + 102, cy - 22), "GND\n(0V)", font=FONT_SMALL_B, fill="#0F172A")
    else:
        draw.chord((cx - cr, c_cy - cr, cx + cr, c_cy + cr), start=125, end=235, fill="#111827")
        draw.text((cx - 28, c_cy - 14), "-", font=FONT_PANEL_HDR, fill="#FFFFFF")
        draw.text((cx + 13, c_cy - 14), "+", font=FONT_PANEL_HDR, fill="#0F172A")
        draw.text((cx - 164, cy - 30), "v_minus\n(-16V)", font=FONT_SMALL_B, fill="#0F172A")
        draw.text((cx + 102, cy - 22), "GND\n(0V)", font=FONT_SMALL_B, fill="#15803D")

    # Silkscreen '+' indicator placed clearly below the left pad (no overlap with base)
    draw.text((cx - 122, cy + 28), "PCB '+'", font=FONT_SMALL_B, fill="#B45309")

    if wrong:
        draw.text((cx - 156, cy + 68), "X  16V REVERSE BIAS (DESTRUCTIVE)", font=FONT_SMALL_B, fill="#B91C1C")
    else:
        draw.text((cx - 150, cy + 68), "OK  IGNORE PCB '+' MARK ON C3 & C27", font=FONT_SMALL_B, fill="#15803D")


def draw_panel1_locator(canvas, draw, ov_img, ov_mm):
    box = (24, 160, 1410, 1050)
    draw_panel_frame(draw, box, "1. CARRIER BOARD LOCATOR MAP  (TOP VIEW / F.Cu — UPRIGHT AS INSTALLED)", "#3B82F6")

    # Place PCB overview in left portion of Panel 1 leaving clean callout column on right
    target_w = 860
    target_h = int(round(ov_img.height * (target_w / ov_img.width)))
    if target_h > 675:
        target_h = 675
        target_w = int(round(ov_img.width * (target_h / ov_img.height)))
    ov_res = ov_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    pcb_x0 = box[0] + 64
    pcb_y0 = box[1] + 108
    pcb_box = (pcb_x0, pcb_y0, pcb_x0 + target_w, pcb_y0 + target_h)
    canvas.paste(ov_res, (pcb_x0, pcb_y0))
    draw.rectangle(pcb_box, outline="#334155", width=2)

    # Edge orientation helpers
    draw.text((pcb_x0 + 230, pcb_y0 - 30), "^ TOP EDGE  (MH1,  J1 Pin 1 Chassis GND)", font=FONT_SMALL_B, fill="#0F172A")
    draw.text((pcb_x0 + 230, pcb_box[3] + 10), "v BOTTOM EDGE  (MH2,  J1 Pin 15 +48V)", font=FONT_SMALL_B, fill="#0F172A")
    draw.text((pcb_x0 - 44, pcb_y0 + target_h // 2 - 42), "F\nA\nC\nE", font=FONT_SMALL_B, fill="#334155")
    draw.text((pcb_box[2] - 115, pcb_y0 - 30), "500 EDGE ->", font=FONT_SMALL_B, fill="#334155")

    # Right column callout stack (top-to-bottom matching real Y order, staggered leader channels)
    targets = [
        ("[5]", (157.800, 73.950), 9.0, 8.0, "#7C3AED", "U4 (THAT1646S08-U)", "DEAD-BUG ALL 8 WIRES", "Panel 4: Belly-up, notch TOP", 10),
        ("[3]", (151.000, 94.350), 5.0, 5.0, "#DC2626", "D11 (BAT54S Clamp)", "DESOLDER & REMOVE", "Clips neg. audio at -0.3V", 18),
        ("[2]", (145.450, 98.200), 10.5, 8.5, "#DC2626", "C27 (220uF -16V)", "ROTATE 180° ON PADS", "Backwards on -16V (keep C26!)", 26),
        ("[4]", (158.250, 115.436), 9.0, 8.5, "#2563EB", "U2 (THAT1200S08-U)", "SOLDER PINS 1-5, LIFT 3", "Panel 3: Jumper Pins 6, 7, 8", 34),
        ("[!]", (175.650, 115.936), 5.5, 11.0, "#D97706", "C12 & C13 (10uF 10V)", "BENCH SIGNAL < +/-8Vpk", "10V X5R caps; NO +48V!", 42),
        ("[1]", (176.067, 145.085), 10.5, 8.5, "#DC2626", "C3 (220uF -16V)", "ROTATE 180° ON PADS", "Backwards on -16V (keep C1!)", 18),
    ]

    cx_card0 = pcb_box[2] + 56
    cx_card1 = box[2] - 20
    cy_positions = [245, 368, 491, 614, 737, 860]

    for (tag, (wx, wy), bw_mm, bh_mm, col, title, action, note, lane_dx), card_y in zip(targets, cy_positions):
        tx, ty = mm_to_px(wx, wy, ov_mm, pcb_box)
        hw = int(round((bw_mm / 2.0) / (ov_mm[2] - ov_mm[0]) * target_w))
        hh = int(round((bh_mm / 2.0) / (ov_mm[3] - ov_mm[1]) * target_h))
        # Highlight box on PCB
        draw.rectangle((tx - hw, ty - hh, tx + hw, ty + hh), outline=col, width=3)
        draw.ellipse((tx - 5, ty - 5, tx + 5, ty + 5), fill=col, outline="#FFFFFF")

        # Callout card on right
        cy0, cy1 = card_y - 16, card_y + 84
        draw_round_rect(draw, (cx_card0, cy0, cx_card1, cy1), 10, fill="#F8FAFC", outline=col, width=3)
        draw_badge(draw, cx_card0 + 26, cy0 + 24, tag, bg=col, w=40, h=30)
        draw.text((cx_card0 + 54, cy0 + 10), title, font=FONT_BODY_B, fill="#0F172A")
        draw.text((cx_card0 + 14, cy0 + 44), action, font=FONT_SMALL_B, fill=col)
        draw.text((cx_card0 + 14, cy0 + 68), note, font=FONT_SMALL, fill="#475569")

        # Staggered orthogonal leader from PCB highlight right edge to card left edge
        card_mid_y = (cy0 + cy1) // 2
        elbow_x = pcb_box[2] + lane_dx
        draw.line([(tx + hw, ty), (elbow_x, ty), (elbow_x, card_mid_y), (cx_card0, card_mid_y)], fill=col, width=3)

    # Bottom-right summary legend note
    draw_round_rect(draw, (cx_card0, 962, cx_card1, 1032), 10, fill="#ECFDF5", outline="#10B981", width=2)
    draw.text((cx_card0 + 14, 972), "VERIFIED GOOD: C1, C25, C26, U1 (TSR1), U3 (TL072),", font=FONT_SMALL_B, fill="#065F46")
    draw.text((cx_card0 + 14, 996), "D1-D10, J1 edge pins, U6 & J_ENC alignment.", font=FONT_SMALL, fill="#065F46")


def draw_panel2_prepower(canvas, draw, c3_pack, c27_pack):
    box = (1434, 160, 2776, 1050)
    draw_panel_frame(draw, box, "2. PRE-POWER FIXES:  ROTATE [1] C3 & [2] C27 180°   |   REMOVE [3] D11", "#DC2626")

    c3_img, c3_mm = c3_pack
    c27_img, c27_mm = c27_pack

    # Top row: Two real zoomed PCB crops side by side
    crop_w, crop_h = 560, 380
    c3_res = c3_img.resize((crop_w, crop_h), Image.Resampling.LANCZOS)
    c27_res = c27_img.resize((crop_w, crop_h), Image.Resampling.LANCZOS)

    b1 = (box[0] + 36, box[1] + 92, box[0] + 36 + crop_w, box[1] + 92 + crop_h)
    b2 = (box[0] + 746, box[1] + 92, box[0] + 746 + crop_w, box[1] + 92 + crop_h)

    draw.text((b1[0], b1[1] - 26), "PCB ZOOM A:  C3 near U1 / D2 (Bottom-Right Corner)", font=FONT_BODY_B, fill="#0F172A")
    draw.text((b2[0], b2[1] - 26), "PCB ZOOM B:  C27 & D11 near U3 (Mid-Right Section)", font=FONT_BODY_B, fill="#0F172A")

    canvas.paste(c3_res, (b1[0], b1[1]))
    canvas.paste(c27_res, (b2[0], b2[1]))
    draw.rectangle(b1, outline="#334155", width=3)
    draw.rectangle(b2, outline="#334155", width=3)

    # Overlay crisp annotations onto Zoom A (C3)
    c3_px, c3_py = mm_to_px(176.067, 145.085, c3_mm, b1)
    draw.rectangle((c3_px - 95, c3_py - 68, c3_px + 95, c3_py + 68), outline="#EF4444", width=4)
    draw_badge(draw, c3_px, c3_py - 84, "[1] C3: FLIP 180°", bg="#DC2626", w=170, h=28)
    draw.text((c3_px - 108, c3_py + 72), "Pad1(-16V)    Pad2(GND)", font=FONT_SMALL_B, fill="#FEF08A")

    # Overlay crisp annotations onto Zoom B (C26 OK, C27 Flip, D11 Remove)
    c26_px, c26_py = mm_to_px(145.500, 89.300, c27_mm, b2)
    draw.rectangle((c26_px - 88, c26_py - 56, c26_px + 88, c26_py + 56), outline="#22C55E", width=4)
    draw_badge(draw, c26_px + 125, c26_py - 46, "C26: KEEP (+16V)", bg="#15803D", w=175, h=26)

    c27_px, c27_py = mm_to_px(145.450, 98.200, c27_mm, b2)
    draw.rectangle((c27_px - 88, c27_py - 56, c27_px + 88, c27_py + 56), outline="#EF4444", width=4)
    draw_badge(draw, c27_px, c27_py + 72, "[2] C27: FLIP 180°", bg="#DC2626", w=170, h=28)

    d11_px, d11_py = mm_to_px(151.000, 94.350, c27_mm, b2)
    draw.rectangle((d11_px - 42, d11_py - 36, d11_px + 42, d11_py + 36), outline="#EF4444", width=4)
    draw.line([(d11_px - 32, d11_py - 28), (d11_px + 32, d11_py + 28)], fill="#EF4444", width=5)
    draw.line([(d11_px - 32, d11_py + 28), (d11_px + 32, d11_py - 28)], fill="#EF4444", width=5)
    draw_badge(draw, d11_px + 135, d11_py + 62, "[3] D11: REMOVE", bg="#DC2626", w=165, h=28)
    draw.line([(d11_px + 36, d11_py + 28), (d11_px + 74, d11_py + 48)], fill="#EF4444", width=3)

    # Bottom row left/center: Before -> After Capacitor Rotation Visual
    draw.text((box[0] + 36, 650), "C3 & C27 POLARITY FIX (BOTH ARE IDENTICAL 220uF / 25V CANS):", font=FONT_H3, fill="#0F172A")
    draw_cap_icon(draw, box[0] + 216, 760, plus_on_left=True, wrong=True)
    # Arrow between Before and After
    ax0, ax1, ay = box[0] + 406, box[0] + 494, 764
    draw.line([(ax0, ay), (ax1 - 14, ay)], fill="#0F172A", width=8)
    draw.polygon([(ax1, ay), (ax1 - 24, ay - 16), (ax1 - 24, ay + 16)], fill="#0F172A")
    draw.text((ax0 + 2, ay - 46), "ROTATE\n  180°", font=FONT_SMALL_B, fill="#0F172A")
    draw_cap_icon(draw, box[0] + 684, 760, plus_on_left=False, wrong=False)

    # Safe rails reminder box under cap icons
    draw_round_rect(draw, (box[0] + 36, 872, box[0] + 850, 944), 10, fill="#DCFCE7", outline="#16A34A", width=2)
    draw.text((box[0] + 54, 883), "DO NOT FLIP C1 (+16V), C25 (+5V), OR C26 (+16V)!", font=FONT_BODY_B, fill="#14532D")
    draw.text((box[0] + 54, 912), "Those three sit on positive rails, so Pad 1 (+) on the positive rail is already correct.", font=FONT_SMALL, fill="#14532D")

    # Bench signal note below that
    draw_round_rect(draw, (box[0] + 36, 958, box[0] + 850, 1026), 10, fill="#FFFBEB", outline="#D97706", width=2)
    draw.text((box[0] + 54, 968), "REV-1 BENCH WARNING — C12, C13 (10V X5R) & U3A HEADROOM:", font=FONT_SMALL_B, fill="#92400E")
    draw.text((box[0] + 54, 994), "Keep bench input below +8 dBu, NEVER connect +48V phantom (C12/C13 are rated 10V!).", font=FONT_SMALL, fill="#78350F")

    # Bottom row right: D11 (BAT54S) detailed removal card
    dx0, dy0, dx1, dy1 = box[0] + 876, 654, box[2] - 32, 1026
    draw_round_rect(draw, (dx0, dy0, dx1, dy1), 12, fill="#FEF2F2", outline="#DC2626", width=3)
    draw_badge(draw, dx0 + 38, dy0 + 32, "[3]", bg="#DC2626", w=44, h=30)
    draw.text((dx0 + 70, dy0 + 20), "DESOLDER & REMOVE D11", font=FONT_H3, fill="#991B1B")
    draw.text((dx0 + 20, dy0 + 56), "Part: BAT54S (SOT-23, between C15 & R11)", font=FONT_SMALL_B, fill="#0F172A")

    # SOT-23 pin drawing with big red X
    scx, scy = (dx0 + dx1) // 2, dy0 + 165
    draw.rectangle((scx - 42, scy - 52, scx + 42, scy + 52), fill="#1E293B", outline="#0F172A", width=3)
    draw.rectangle((scx - 74, scy - 40, scx - 42, scy - 16), fill="#CBD5E1", outline="#475569")
    draw.rectangle((scx - 74, scy + 16, scx - 42, scy + 40), fill="#CBD5E1", outline="#475569")
    draw.rectangle((scx + 42, scy - 12, scx + 74, scy + 12), fill="#CBD5E1", outline="#475569")
    draw.text((scx - 180, scy - 40), "Pin 1 (GND)", font=FONT_SMALL_B, fill="#B91C1C")
    draw.text((scx - 190, scy + 18), "Pin 2 (+3.3V)", font=FONT_SMALL_B, fill="#475569")
    draw.text((scx + 82, scy - 20), "Pin 3\ndaisy_audio_in", font=FONT_SMALL_B, fill="#0F172A")
    draw.line([(scx - 56, scy - 58), (scx + 56, scy + 58)], fill="#EF4444", width=7)
    draw.line([(scx - 56, scy + 58), (scx + 56, scy - 58)], fill="#EF4444", width=7)

    draw.text((dx0 + 20, dy0 + 245), "WHY REMOVE:", font=FONT_SMALL_B, fill="#991B1B")
    draw.text((dx0 + 20, dy0 + 270), "Daisy Pin 16 expects 0V-centered AC audio.", font=FONT_SMALL, fill="#0F172A")
    draw.text((dx0 + 20, dy0 + 294), "D11.1 (to GND) clips the entire negative", font=FONT_SMALL, fill="#0F172A")
    draw.text((dx0 + 20, dy0 + 318), "half-wave flat at -0.3V (~-4.4 dBu in).", font=FONT_SMALL, fill="#0F172A")
    draw.text((dx0 + 20, dy0 + 344), "LEAVE PADS EMPTY FOR BENCH TESTS.", font=FONT_SMALL_B, fill="#991B1B")


def draw_panel3_u2(draw):
    box = (24, 1074, 1410, 1976)
    draw_panel_frame(draw, box, "3. [4] U2 (THAT1200S08-U) — PARTIAL PIN-LIFT  (SOLDER PINS 1–5 FLAT, ONLY 3 WIRES)", "#2563EB")

    # Left side: Exact upright PCB footprint diagram (U2 is rotated 180 deg -> Pin 1 is BOTTOM-RIGHT!)
    diag_x0, diag_y0, diag_x1, diag_y1 = box[0] + 24, box[1] + 68, box[0] + 748, box[1] + 884
    draw_round_rect(draw, (diag_x0, diag_y0, diag_x1, diag_y1), 12, fill="#1E293B", outline="#334155", width=2)
    draw.text((diag_x0 + 18, diag_y0 + 14), "EXACT UPRIGHT PCB ORIENTATION (U2 IS ROTATED 180°)", font=FONT_BODY_B, fill="#F8FAFC")
    draw.text((diag_x0 + 18, diag_y0 + 40), "Chip is RIGHT-SIDE UP (legs down)  |  PIN 1 DOT AT BOTTOM-RIGHT", font=FONT_SMALL_B, fill="#93C5FD")

    # Pad geometry (centered to give wide Kapton + wire bus clearance on LEFT AND right label margin)
    cx, cy = diag_x0 + 372, diag_y0 + 425
    row_ys = [cy - 200, cy - 68, cy + 64, cy + 196]  # top -> bottom

    # Draw Kapton tape strip underneath Pads 6, 7, 8 (Left col, rows 1, 2, 3)
    kap_box = (cx - 210, row_ys[1] - 42, cx - 80, row_ys[3] + 42)
    draw_round_rect(draw, kap_box, 8, fill="#92400E", outline="#F59E0B", width=3)
    draw.text((kap_box[0] - 12, kap_box[3] + 12), "KAPTON TAPE OVER INNER", font=FONT_SMALL_B, fill="#FBBF24")
    draw.text((kap_box[0] - 12, kap_box[3] + 32), "2/3 OF PADS 6, 7, 8", font=FONT_SMALL_B, fill="#FBBF24")

    # Left PCB pads: row0=Pad5(sm), row1=Pad6(cm), row2=Pad7(audio_out), row3=Pad8(v_plus)
    left_pads = [
        ("Pad 5", "sm", "#22C55E", True),
        ("Pad 6", "cm", "#EA580C", False),
        ("Pad 7", "audio_out", "#3B82F6", False),
        ("Pad 8", "v_plus (+16V)", "#EF4444", False),
    ]
    # Right PCB pads (top->bottom): row0=Pad4(v_minus), row1=Pad3(in_plus), row2=Pad2(in_minus), row3=Pad1(gnd)
    right_pads = [
        ("Pad 4", "v_minus (-16V)", "#22C55E"),
        ("Pad 3", "in_plus", "#22C55E"),
        ("Pad 2", "in_minus", "#22C55E"),
        ("Pad 1", "gnd (REF)", "#22C55E"),
    ]

    pad_h = 42
    # Draw PCB Pads first
    for idx, (pname, pnet, pcol, flat_ok) in enumerate(left_pads):
        py = row_ys[idx]
        px0, px1 = cx - 255, cx - 125
        if not flat_ok:
            # Left 45px exposed copper tip, inner 85px covered by amber Kapton tape
            draw.rectangle((px0, py - pad_h // 2, px0 + 44, py + pad_h // 2), fill="#D8B4FE", outline="#F8FAFC", width=2)
            draw.rectangle((px0 + 44, py - pad_h // 2, px1, py + pad_h // 2), fill="#B45309", outline="#F59E0B", width=2)
        else:
            draw.rectangle((px0, py - pad_h // 2, px1, py + pad_h // 2), fill="#BBF7D0", outline="#22C55E", width=3)
        draw.text((px0 - 108, py - 20), f"{pname}\n{pnet}", font=FONT_SMALL_B, fill="#E2E8F0")

    for idx, (pname, pnet, pcol) in enumerate(right_pads):
        py = row_ys[idx]
        px0, px1 = cx + 110, cx + 225
        draw.rectangle((px0, py - pad_h // 2, px1, py + pad_h // 2), fill="#BBF7D0", outline="#22C55E", width=3)
        draw.text((px1 + 12, py - 20), f"{pname}\n{pnet}", font=FONT_SMALL_B, fill="#BBF7D0")

    # Draw THAT1200 IC package (right-side up, Pin 1 dot BOTTOM-RIGHT)
    ic_box = (cx - 95, row_ys[0] - 58, cx + 95, row_ys[3] + 58)
    draw_round_rect(draw, ic_box, 10, fill="#0F172A", outline="#94A3B8", width=3)
    draw.ellipse((ic_box[2] - 32, ic_box[3] - 32, ic_box[2] - 12, ic_box[3] - 12), fill="#F8FAFC")
    draw.text((cx - 56, cy - 42), "THAT1200\n S08-U", font=FONT_H3, fill="#F8FAFC")
    draw.text((cx - 72, cy + 16), "TOP FACE UP\nPin 1 Dot BR", font=FONT_SMALL_B, fill="#94A3B8")

    # Draw IC leads (Pins 1-4 right, Pin 5 top-left, LIFTED Pins 6-8 left)
    for idx, pnum in enumerate(["4 (Vee)", "3 (In+)", "2 (In-)", "1 (Ref)"]):
        py = row_ys[idx]
        draw.rectangle((ic_box[2], py - 14, cx + 165, py + 14), fill="#4ADE80", outline="#14532D", width=2)
        draw.text((ic_box[2] - 68, py - 10), pnum, font=FONT_SMALL_B, fill="#86EFAC")

    # Pin 5 flat (top-left)
    py5 = row_ys[0]
    draw.rectangle((cx - 175, py5 - 14, ic_box[0], py5 + 14), fill="#4ADE80", outline="#14532D", width=2)
    draw.text((ic_box[0] + 10, py5 - 10), "5 (CMIn)", font=FONT_SMALL_B, fill="#86EFAC")

    # Lifted Pins 6, 7, 8 (left col, rows 1, 2, 3) hovering cleanly at cx - 142 above Kapton zone
    lifted = [
        (1, "6 (Vout)", "#38BDF8", "#0284C7"),
        (2, "7 (Vcc)", "#FCA5A5", "#DC2626"),
        (3, "8 (CMOut)", "#FDBA74", "#EA580C"),
    ]
    pin_tips_y = {}
    for row_i, lbl, fg, bg in lifted:
        py = row_ys[row_i]
        draw_round_rect(draw, (cx - 142, py - 16, ic_box[0] + 4, py + 16), 4, fill=bg, outline="#FFFFFF", width=2)
        draw.text((ic_box[0] + 10, py - 10), lbl, font=FONT_SMALL_B, fill=fg)
        pin_tips_y[row_i] = (cx - 142, py)

    # Outer exposed purple pad tips sit at [cx - 255 .. cx - 211]; target wire solder point cx - 230
    # Clear Kapton wire lane is [cx - 208 .. cx - 144] (64 px wide, 3 separate X lanes!)
    pad_tips = {
        1: (cx - 228, row_ys[1]),  # Pad 6 (cm)
        2: (cx - 228, row_ys[2]),  # Pad 7 (audio_out)
        3: (cx - 228, row_ys[3]),  # Pad 8 (v_plus)
    }

    # 1) BLUE: Pin 6 (row 1) -> lane cx-156 -> Pad 7 tip (row 2)
    p6x, p6y = pin_tips_y[1]
    t7x, t7y = pad_tips[2]
    draw.line([(p6x, p6y - 4), (cx - 156, p6y - 4), (cx - 156, t7y - 10), (t7x, t7y - 10)], fill="#38BDF8", width=6)
    draw.ellipse((p6x - 5, p6y - 9, p6x + 5, p6y + 1), fill="#FFFFFF", outline="#0284C7", width=2)
    draw.ellipse((t7x - 6, t7y - 16, t7x + 6, t7y - 4), fill="#38BDF8", outline="#FFFFFF", width=2)

    # 2) RED: Pin 7 (row 2) -> lane cx-176 -> Pad 8 tip (row 3)
    p7x, p7y = pin_tips_y[2]
    t8x, t8y = pad_tips[3]
    draw.line([(p7x, p7y + 2), (cx - 176, p7y + 2), (cx - 176, t8y), (t8x, t8y)], fill="#EF4444", width=6)
    draw.ellipse((p7x - 5, p7y - 3, p7x + 5, p7y + 7), fill="#FFFFFF", outline="#DC2626", width=2)
    draw.ellipse((t8x - 6, t8y - 6, t8x + 6, t8y + 6), fill="#EF4444", outline="#FFFFFF", width=2)

    # 3) ORANGE: Pin 8 (row 3) -> down slightly -> lane cx-196 -> UP to Pad 6 tip (row 1)
    p8x, p8y = pin_tips_y[3]
    t6x, t6y = pad_tips[1]
    draw.line([(p8x, p8y + 12), (cx - 196, p8y + 12), (cx - 196, t6y), (t6x, t6y)], fill="#FB923C", width=6)
    draw.ellipse((p8x - 5, p8y + 7, p8x + 5, p8y + 17), fill="#FFFFFF", outline="#EA580C", width=2)
    draw.ellipse((t6x - 6, t6y - 6, t6x + 6, t6y + 6), fill="#FB923C", outline="#FFFFFF", width=2)

    draw.text((diag_x0 + 20, diag_y1 - 44), "GREEN PADS = MATCH 1:1 (SOLDER FLAT)", font=FONT_SMALL_B, fill="#86EFAC")

    # Right half of Panel 3: Step-by-Step Instructions + Wiring Table + Continuity Test
    rx0, ry0, rx1 = box[0] + 768, box[1] + 68, box[2] - 24
    draw_round_rect(draw, (rx0, ry0, rx1, ry0 + 225), 12, fill="#F8FAFC", outline="#CBD5E1", width=2)
    draw.text((rx0 + 18, ry0 + 14), "STEP-BY-STEP ASSEMBLY (U2 THAT1200S08-U)", font=FONT_H3, fill="#0F172A")
    steps = [
        "1. Put Kapton tape over inner 2/3 of PCB Pads 6, 7, 8 (leave",
        "   outer copper pad tips exposed). Leave Pads 1–5 bare.",
        "2. Gently bend IC Pins 6, 7, 8 UP ~15° before placing chip.",
        "3. Orient chip RIGHT-SIDE UP with Pin 1 dot BOTTOM-RIGHT.",
        "4. Solder Pins 1–5 FLAT onto Pads 1–5 (direct 1:1 match).",
        "5. Solder the 3 short 30 AWG jumper wires shown below:",
    ]
    for i, s in enumerate(steps):
        draw.text((rx0 + 18, ry0 + 50 + i * 27), s, font=FONT_BODY, fill="#1E293B")

    # Wiring table
    ty0 = ry0 + 242
    draw_round_rect(draw, (rx0, ty0, rx1, ty0 + 265), 12, fill="#EFF6FF", outline="#2563EB", width=3)
    draw.text((rx0 + 18, ty0 + 14), "U2 JUMPER WIRE TABLE (3 WIRES ONLY)", font=FONT_H3, fill="#1E3A8A")
    headers = ("WIRE", "IC PIN (LIFTED)", "-> PCB PAD", "NET NAME")
    xs = [rx0 + 18, rx0 + 110, rx0 + 300, rx0 + 445]
    for h, x in zip(headers, xs):
        draw.text((x, ty0 + 48), h, font=FONT_SMALL_B, fill="#1E40AF")
    draw.line([(rx0 + 16, ty0 + 70), (rx1 - 16, ty0 + 70)], fill="#93C5FD", width=2)

    u2_rows = [
        ("BLUE", "Pin 6  (Vout)", "Pad 7", "audio_out -> R3", "#0284C7"),
        ("RED", "Pin 7  (Vcc +16V)", "Pad 8", "v_plus (+16V)", "#DC2626"),
        ("ORANGE", "Pin 8  (CM Out)", "Pad 6", "cm -> C14.1", "#EA580C"),
    ]
    for r_i, (wcol, pin_s, pad_s, net_s, hex_c) in enumerate(u2_rows):
        ry = ty0 + 84 + r_i * 58
        draw_round_rect(draw, (xs[0], ry, xs[0] + 78, ry + 36), 6, fill=hex_c)
        draw.text((xs[0] + 10, ry + 7), wcol, font=FONT_SMALL_B, fill="#FFFFFF")
        draw.text((xs[1], ry + 6), pin_s, font=FONT_BODY_B, fill="#0F172A")
        draw.text((xs[2], ry + 6), pad_s, font=FONT_BODY_B, fill="#0F172A")
        draw.text((xs[3], ry + 6), net_s, font=FONT_MONO_B, fill="#334155")

    # Multimeter verification box
    my0 = ty0 + 282
    draw_round_rect(draw, (rx0, my0, rx1, diag_y1), 12, fill="#FEF3C7", outline="#D97706", width=2)
    draw.text((rx0 + 18, my0 + 14), "MULTIMETER CHECK BEFORE POWERING UP U2:", font=FONT_BODY_B, fill="#92400E")
    checks = [
        "• BEEP (0 ohm): IC Pin 7 <-> D1 (+16V rail v_plus)",
        "• BEEP (0 ohm): IC Pin 6 <-> R3.1  |  IC Pin 8 <-> C14.1",
        "• NO SHORT: IC Pin 8 (CM Out) <-> v_plus (+16V) must be OPEN!",
        "• NO SHORT: IC Pin 6 <-> Pad 6,  Pin 7 <-> Pad 7,  Pin 8 <-> Pad 8",
    ]
    for i, c in enumerate(checks):
        draw.text((rx0 + 18, my0 + 48 + i * 28), c, font=FONT_BODY, fill="#78350F")


def draw_panel4_u4(draw):
    box = (1434, 1074, 2776, 1976)
    draw_panel_frame(draw, box, "4. [5] U4 (THAT1646S08-U or DIP-8 1646P08-U) — FULL DEAD-BUG (ALL 8 WIRES)", "#7C3AED")

    # Left side: Exact upright PCB footprint + belly-up chip orientation (U4 rot=0 -> Pad 1 TOP-LEFT!)
    diag_x0, diag_y0, diag_x1, diag_y1 = box[0] + 24, box[1] + 68, box[0] + 730, box[1] + 884
    draw_round_rect(draw, (diag_x0, diag_y0, diag_x1, diag_y1), 12, fill="#1E293B", outline="#334155", width=2)
    draw.text((diag_x0 + 18, diag_y0 + 14), "EXACT UPRIGHT PCB PADS (U4 0° -> PAD 1 TOP-LEFT)", font=FONT_BODY_B, fill="#F8FAFC")
    draw.text((diag_x0 + 18, diag_y0 + 40), "CHIP MOUNTED BELLY-UP (LEGS UP) + NOTCH AT TOP -> PIN 1 TOP-RIGHT!", font=FONT_SMALL_B, fill="#DDD6FE")

    cx, cy = diag_x0 + 352, diag_y0 + 438
    row_ys = [cy - 195, cy - 65, cy + 65, cy + 195]  # top -> bottom

    # Outer PCB pads pushed wider to give 74 px wire corridors on BOTH sides!
    left_pads = [
        ("Pad 1", "out_plus", "#22C55E"),
        ("Pad 2", "v_minus (-16V)", "#EF4444"),
        ("Pad 3", "out_minus", "#F59E0B"),
        ("Pad 4", "gnd", "#94A3B8"),
    ]
    right_pads = [
        ("Pad 8", "sense_plus", "#A855F7"),
        ("Pad 7", "sense_minus", "#14B8A6"),
        ("Pad 6", "v_plus (+16V)", "#F43F5E"),
        ("Pad 5", "to_1646 (U3.7)", "#38BDF8"),
    ]

    for idx, (pname, pnet, pcol) in enumerate(left_pads):
        py = row_ys[idx]
        px0, px1 = diag_x0 + 132, diag_x0 + 188
        draw.rectangle((px0, py - 21, px1, py + 21), fill="#D8B4FE", outline="#F8FAFC", width=2)
        draw.text((diag_x0 + 14, py - 20), f"{pname}\n{pnet}", font=FONT_SMALL_B, fill="#E2E8F0")

    for idx, (pname, pnet, pcol) in enumerate(right_pads):
        py = row_ys[idx]
        px0, px1 = diag_x0 + 516, diag_x0 + 572
        draw.rectangle((px0, py - 21, px1, py + 21), fill="#D8B4FE", outline="#F8FAFC", width=2)
        draw.text((px1 + 10, py - 20), f"{pname}\n{pnet}", font=FONT_SMALL_B, fill="#E2E8F0")

    # Kapton pad island under belly-up IC
    draw_round_rect(draw, (cx - 102, row_ys[0] - 58, cx + 102, row_ys[3] + 58), 10, fill="#92400E", outline="#F59E0B", width=3)

    # Belly-up IC body (notch at top, Pin 1 dot TOP-RIGHT!)
    ic_box = (cx - 66, row_ys[0] - 46, cx + 66, row_ys[3] + 46)
    draw_round_rect(draw, ic_box, 10, fill="#0F172A", outline="#C4B5FD", width=3)
    draw.arc((cx - 16, ic_box[1] - 14, cx + 16, ic_box[1] + 14), start=0, end=180, fill="#C4B5FD", width=3)
    draw.ellipse((ic_box[2] - 28, ic_box[1] + 10, ic_box[2] - 10, ic_box[1] + 28), fill="#FDE047")

    draw.text((cx - 48, cy - 26), "THAT1646\nBELLY-UP", font=FONT_BODY_B, fill="#F8FAFC")
    draw.text((cx - 46, cy + 20), "Pin 1 = TR", font=FONT_SMALL_B, fill="#FDE047")

    # Belly-up chip pins sticking out Left & Right (22 px wide -> tips at cx +/- 88)
    bu_left = ["8 Out+", "7 Sns+", "6 Vcc", "5 Vee"]
    bu_right = ["1 Out-", "2 Sns-", "3 Gnd", "4 In"]
    l_pts = []
    r_pts = []
    for idx in range(4):
        py = row_ys[idx]
        draw.rectangle((ic_box[0] - 22, py - 11, ic_box[0], py + 11), fill="#E2E8F0", outline="#64748B", width=2)
        draw.text((ic_box[0] + 6, py - 9), bu_left[idx], font=FONT_SMALL_B, fill="#F8FAFC")
        l_pts.append((ic_box[0] - 22, py))

        draw.rectangle((ic_box[2], py - 11, ic_box[2] + 22, py + 11), fill="#E2E8F0", outline="#64748B", width=2)
        draw.text((ic_box[2] - 54, py - 9), bu_right[idx], font=FONT_SMALL_B, fill="#FDE047" if idx == 0 else "#F8FAFC")
        r_pts.append((ic_box[2] + 22, py))

    # PCB inner pad edges for wires: left = diag_x0 + 188, right = diag_x0 + 516
    pcb_l = [(diag_x0 + 188, row_ys[i]) for i in range(4)]  # Pad 1, 2, 3, 4
    pcb_r = [(diag_x0 + 516, row_ys[i]) for i in range(4)]  # Pad 8, 7, 6, 5

    # Spacious corridors: Left [diag_x0+188 .. cx-88] = 76 px wide! Right [cx+88 .. diag_x0+516] = 76 px wide!
    # 3 STRAIGHT ADJACENT ZERO-CROSSING WIRES:
    draw.line([l_pts[0], pcb_l[0]], fill="#22C55E", width=6)   # Pin 8 -> Pad 1 (out_plus)
    draw.line([r_pts[1], pcb_r[1]], fill="#14B8A6", width=6)   # Pin 2 -> Pad 7 (sense_minus)
    draw.line([r_pts[3], pcb_r[3]], fill="#38BDF8", width=6)   # Pin 4 -> Pad 5 (in)

    # 1 SAME-SIDE WIRE (Pin 5 -> Pad 2 via left outer lane x = l_pts[3][0] - 22):
    l_lane1 = l_pts[3][0] - 22
    draw.line([l_pts[3], (l_lane1, l_pts[3][1]), (l_lane1, pcb_l[1][1]), pcb_l[1]], fill="#EF4444", width=5)

    # 4 CROSS-BODY ARCHED WIRES (wide lanes above & below Kapton, ZERO wire crossing text!):
    # W5: Pin 7 (l_pts[1]) -> Pad 8 (pcb_r[0]) arched OVER top notch (y = ic_box[1] - 26)
    top_y1 = ic_box[1] - 26
    draw.line([(l_pts[1][0], l_pts[1][1] - 4), (l_lane1, l_pts[1][1] - 4), (l_lane1, top_y1), (pcb_r[0][0] - 20, top_y1), pcb_r[0]], fill="#C084FC", width=5)

    # W6: Pin 1 (r_pts[0]) -> Pad 3 (pcb_l[2]) over higher top lane (top_y2) then down inner left lane (pcb_l[2][0] + 18)
    top_y2 = ic_box[1] - 48
    r_lane1 = r_pts[0][0] + 22
    l_lane2 = pcb_l[2][0] + 22
    draw.line([(r_pts[0][0], r_pts[0][1] - 4), (r_lane1, r_pts[0][1] - 4), (r_lane1, top_y2), (l_lane2, top_y2), (l_lane2, pcb_l[2][1]), pcb_l[2]], fill="#F59E0B", width=5)

    # W7: Pin 3 (r_pts[2]) -> Pad 4 (pcb_l[3]) under BOTTOM edge (bot_y1 = ic_box[3] + 24)
    bot_y1 = ic_box[3] + 24
    draw.line([(r_pts[2][0], r_pts[2][1] + 4), (r_lane1, r_pts[2][1] + 4), (r_lane1, bot_y1), (pcb_l[3][0] + 22, bot_y1), pcb_l[3]], fill="#E2E8F0", width=5)

    # W8: Pin 6 (l_pts[2]) -> Pad 6 (pcb_r[2]) under lower bottom lane (bot_y2 = ic_box[3] + 46)
    bot_y2 = ic_box[3] + 46
    l_lane_inner = l_pts[2][0] - 10
    r_lane2 = pcb_r[2][0] - 22
    draw.line([(l_pts[2][0], l_pts[2][1] + 6), (l_lane_inner, l_pts[2][1] + 6), (l_lane_inner, bot_y2), (r_lane2, bot_y2), (r_lane2, pcb_r[2][1]), pcb_r[2]], fill="#FB7185", width=5)

    # Place Kapton label cleanly BELOW bot_y2 so zero wires cross the text!
    draw.text((cx - 88, bot_y2 + 22), "KAPTON TAPE UNDER IC", font=FONT_SMALL_B, fill="#FBBF24")

    # Solder dots on all 8 pins
    for pt in l_pts + r_pts + pcb_l + pcb_r:
        draw.ellipse((pt[0] - 5, pt[1] - 5, pt[0] + 5, pt[1] + 5), fill="#FFFFFF", outline="#0F172A", width=2)

    draw.text((diag_x0 + 18, diag_y1 - 44), "TIP: Same 8-pin pinout for SOIC-8 (1646S08-U) OR DIP-8 (1646P08-U)!", font=FONT_SMALL_B, fill="#C4B5FD")

    # Right half of Panel 4: Complete 8-wire checklist table + notes
    rx0, ry0, rx1 = box[0] + 748, box[1] + 68, box[2] - 24
    draw_round_rect(draw, (rx0, ry0, rx1, ry0 + 510), 12, fill="#FAF5FF", outline="#7C3AED", width=3)
    draw.text((rx0 + 18, ry0 + 14), "U4 DEAD-BUG 8-WIRE CHECKLIST", font=FONT_H3, fill="#4C1D95")

    hdrs = ("IC PIN (BELLY-UP)", "-> PCB PAD", "NET / ROUTING")
    cxs = [rx0 + 18, rx0 + 195, rx0 + 305]
    for h, x in zip(hdrs, cxs):
        draw.text((x, ry0 + 48), h, font=FONT_SMALL_B, fill="#5B21B6")
    draw.line([(rx0 + 16, ry0 + 70), (rx1 - 16, ry0 + 70)], fill="#DDD6FE", width=2)

    u4_rows = [
        ("Pin 8 (Out+)", "Pad 1 (TL)", "out_plus  [DIRECT]", "#22C55E"),
        ("Pin 7 (Sns+)", "Pad 8 (TR)", "sense_plus (C21.2)", "#A855F7"),
        ("Pin 6 (Vcc)", "Pad 6 (R3)", "v_plus (+16V)", "#F43F5E"),
        ("Pin 5 (Vee)", "Pad 2 (L2)", "v_minus (-16V)", "#EF4444"),
        ("Pin 4 (In)", "Pad 5 (BR)", "to_1646  [DIRECT]", "#0284C7"),
        ("Pin 3 (Gnd)", "Pad 4 (BL)", "gnd", "#64748B"),
        ("Pin 2 (Sns-)", "Pad 7 (R2)", "sense_minus [DIRECT]", "#0D9488"),
        ("Pin 1 (Out-)", "Pad 3 (L3)", "out_minus (C22.1)", "#D97706"),
    ]
    for i, (pin_s, pad_s, net_s, dot_c) in enumerate(u4_rows):
        ry = ry0 + 82 + i * 52
        draw_round_rect(draw, (rx0 + 12, ry - 4, rx1 - 12, ry + 38), 6, fill="#FFFFFF" if i % 2 == 0 else "#F3E8FF")
        draw.ellipse((cxs[0], ry + 8, cxs[0] + 16, ry + 24), fill=dot_c)
        draw.text((cxs[0] + 24, ry + 5), pin_s, font=FONT_BODY_B, fill="#0F172A")
        draw.text((cxs[1], ry + 5), pad_s, font=FONT_BODY_B, fill="#4C1D95")
        draw.text((cxs[2], ry + 6), net_s, font=FONT_MONO_SM, fill="#334155")

    # DIP-8 tip + smoke test checks at bottom-right of Panel 4
    ny0 = ry0 + 528
    draw_round_rect(draw, (rx0, ny0, rx1, diag_y1), 12, fill="#FEF3C7", outline="#D97706", width=2)
    draw.text((rx0 + 18, ny0 + 14), "WHY BELLY-UP WITH NOTCH AT TOP?", font=FONT_BODY_B, fill="#92400E")
    notes = [
        "• Keeps 3 wires direct & adjacent: Pin8->Pad1, Pin2->Pad7, Pin4->Pad5.",
        "• Mount on 2 layers of Kapton tape (or glue belly onto Kapton).",
        "• MULTIMETER CHECK BEFORE POWERING ON:",
        "  - Pin 6 <-> D1 (+16V) & Pin 5 <-> D2 (-16V): ~0 ohm",
        "  - NO SHORT: Pad 2 (-16V) to Sns- Pin 2 must be OPEN!",
        "  - Pin 3 <-> GND (0 ohm) | Pin 8 <-> J1.2 | Pin 1 <-> J1.4",
    ]
    for i, n in enumerate(notes):
        draw.text((rx0 + 18, ny0 + 48 + i * 32), n, font=FONT_SMALL_B if i == 2 else FONT_SMALL, fill="#78350F")


def main():
    ov_pack, c3_pack, c27_pack = export_pcb_rasters()
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), "#F1F5F9")
    draw = ImageDraw.Draw(canvas)

    # Top Title & Critical Warning Banner
    draw.rectangle((0, 0, CANVAS_W, 84), fill="#0F172A")
    draw.text((32, 12), "ICIO500 JLC CARRIER BOARD (REV 1)  —  WORKBENCH REWORK & DEAD-BUG VISUAL GUIDE", font=FONT_TITLE, fill="#F8FAFC")
    draw.text((34, 52), "Source: kicad/icio500.kicad_pcb  |  All views drawn in UPRIGHT BOARD ORIENTATION (Faceplate Left, 500 Edge Right, Top = MH1 / J1 Pin 1)", font=FONT_SUBTITLE, fill="#94A3B8")

    draw.rectangle((0, 84, CANVAS_W, 140), fill="#B91C1C")
    draw.text((32, 97), "WARNING: DO NOT PLUG INTO A 500 RACK AS-RECEIVED  —  (1) ROTATE C3 & C27 180°   |   (2) REMOVE D11   |   (3) NEVER SOLDER U2 OR U4 FLAT TO PADS", font=FONT_WARN, fill="#FFFFFF")

    draw_panel1_locator(canvas, draw, ov_pack[0], ov_pack[1])
    draw_panel2_prepower(canvas, draw, c3_pack, c27_pack)
    draw_panel3_u2(draw)
    draw_panel4_u4(draw)

    os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
    canvas.save(OUT_PNG, "PNG", optimize=True)
    print(f"Saved visual rework guide -> {OUT_PNG} ({CANVAS_W}x{CANVAS_H})")


if __name__ == "__main__":
    main()
