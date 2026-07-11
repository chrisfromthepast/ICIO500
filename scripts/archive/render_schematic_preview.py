"""
render_schematic_preview.py
───────────────────────────
Draws a clean block-diagram style schematic preview of the
ICIO500 faceplate logic board using Pillow.

Saved to: views/schematic_preview.png
"""

from PIL import Image, ImageDraw
import math

W, H = 1800, 1100
BG   = (252, 252, 248)
BLK  = (20,  20,  20)
GRY  = (120, 120, 120)
BLUE = (30,  80,  200)
RED  = (200, 30,  30)
GRN  = (30,  150, 60)
ORG  = (220, 120, 0)
GOLD = (180, 140, 30)
WIRE = (30,  80,  200)   # wire colour
PWR  = (200, 30,  30)    # power net colour
SIG  = (20,  20,  20)    # signal label

def box(draw, x, y, w, h, label, sublabel="", color=BLK, bg=(240,240,240), lw=2):
    draw.rounded_rectangle([x,y,x+w,y+h], radius=8, fill=bg, outline=color, width=lw)
    draw.text((x+w//2, y+h//2 - (8 if sublabel else 0)), label,
              fill=color, anchor="mm")
    if sublabel:
        draw.text((x+w//2, y+h//2+14), sublabel, fill=GRY, anchor="mm")

def pin_right(draw, x, y, label, net, net_color=WIRE):
    draw.line([x, y, x+30, y], fill=net_color, width=2)
    draw.text((x+34, y), label, fill=BLK, anchor="lm")
    draw.text((x+34, y+13), net, fill=net_color, anchor="lm")

def pin_left(draw, x, y, label, net, net_color=WIRE):
    draw.line([x-30, y, x, y], fill=net_color, width=2)
    draw.text((x-34, y), label, fill=BLK, anchor="rm")
    draw.text((x-34, y+13), net, fill=net_color, anchor="rm")

def horiz_bus(draw, x1, y, x2, nets, spacing=22, color=WIRE):
    for i, net in enumerate(nets):
        yi = y + i*spacing
        draw.line([x1, yi, x2, yi], fill=color, width=2)
        draw.text(((x1+x2)//2, yi-6), net, fill=color, anchor="mm")

def arrow(draw, x1, y1, x2, y2, color=WIRE, label=""):
    draw.line([x1,y1,x2,y2], fill=color, width=2)
    # arrowhead
    dx, dy = x2-x1, y2-y1
    L = math.sqrt(dx*dx+dy*dy)
    if L > 0:
        ux, uy = dx/L, dy/L
        draw.polygon([
            (x2, y2),
            (x2-8*ux+5*uy, y2-8*uy-5*ux),
            (x2-8*ux-5*uy, y2-8*uy+5*ux)
        ], fill=color)
    if label:
        draw.text(((x1+x2)//2, (y1+y2)//2-10), label, fill=color, anchor="mm")

def main():
    img = Image.new("RGB", (W,H), BG)
    draw = ImageDraw.Draw(img)

    # ── Title ──
    draw.text((W//2, 30), "ICIO500 — Faceplate Logic Board Schematic (Rev 0.1)",
              fill=BLK, anchor="mm")
    draw.line([40, 50, W-40, 50], fill=GRY, width=1)

    # ══════════════════════════════════════════════════
    # J1 — JST-SH Connector (left column)
    # ══════════════════════════════════════════════════
    jx, jy, jw, jh = 60, 120, 180, 260
    box(draw, jx, jy, jw, jh, "J1", "JST-SH 8-pin", color=BLUE, bg=(235,242,255))

    pins_j = [
        ("+3V3", "+3V3", PWR),
        ("GND",  "GND",  GRY),
        ("SDA",  "SDA",  WIRE),
        ("SCL",  "SCL",  WIRE),
        ("ENC_A","ENC_A",GRN),
        ("ENC_B","ENC_B",GRN),
        ("ENC_SW","ENC_SW",GRN),
        ("GND",  "GND",  GRY),
    ]
    for i, (lbl, net, col) in enumerate(pins_j):
        py = jy + 30 + i*28
        pin_right(draw, jx+jw, py, lbl, net, col)

    draw.text((jx+jw//2, jy+jh+14), "← To Daisy", fill=GRY, anchor="mm")

    # ══════════════════════════════════════════════════
    # Power conditioning (ferrite + caps)
    # ══════════════════════════════════════════════════
    # ferrite
    fx = 340; fy = 120
    box(draw, fx, fy, 80, 36, "FB1", "BLM18PG", color=GRY, bg=(245,245,235))
    arrow(draw, jx+jw+64, jy+30, fx, fy+18, PWR, "+3V3")
    arrow(draw, fx+80, fy+18, fx+160, fy+18, PWR, "+3V3_CLEAN")

    # C1
    box(draw, fx, fy+55, 60, 32, "C1 10µF", color=GRY, bg=(245,245,235))
    draw.line([fx+30, fy+55, fx+30, fy+87], fill=GRY, width=2)
    draw.text((fx+30, fy+100), "GND", fill=GRY, anchor="mm")

    # C2
    box(draw, fx+80, fy+55, 60, 32, "C2 100nF", color=GRY, bg=(245,245,235))
    draw.line([fx+110, fy+55, fx+110, fy+87], fill=GRY, width=2)
    draw.text((fx+110, fy+100), "GND", fill=GRY, anchor="mm")

    # ══════════════════════════════════════════════════
    # I2C pull-ups
    # ══════════════════════════════════════════════════
    pux = 340; puy = 250
    draw.text((pux+60, puy-20), "I2C Pull-ups", fill=GRY, anchor="mm")
    box(draw, pux,    puy, 60, 30, "R11 4.7k", color=GRY, bg=(245,245,235))
    box(draw, pux+80, puy, 60, 30, "R12 4.7k", color=GRY, bg=(245,245,235))
    # top to +3V3
    for rx in [pux+30, pux+110]:
        draw.line([rx, puy, rx, puy-20], fill=PWR, width=2)
        draw.text((rx, puy-26), "+3V3", fill=PWR, anchor="mm")
    # bottom to SDA/SCL
    draw.line([pux+30, puy+30, pux+30, puy+55], fill=WIRE, width=2)
    draw.text((pux+30, puy+62), "SDA", fill=WIRE, anchor="mm")
    draw.line([pux+110, puy+30, pux+110, puy+55], fill=WIRE, width=2)
    draw.text((pux+110, puy+62), "SCL", fill=WIRE, anchor="mm")

    # ══════════════════════════════════════════════════
    # U1 — IS31FL3236 LED Driver (centre)
    # ══════════════════════════════════════════════════
    ux, uy, uw, uh = 600, 120, 240, 400
    box(draw, ux, uy, uw, uh, "U1  IS31FL3236",
        "36-ch I2C LED Driver\nSSSOP-36", color=(100,0,150), bg=(248,235,255), lw=3)

    # Left pins (inputs)
    left_pins = [
        ("VCC",    "+3V3_CLEAN", PWR),
        ("GND",    "GND",        GRY),
        ("SDA",    "SDA",        WIRE),
        ("SCL",    "SCL",        WIRE),
        ("/SDB",   "+3V3",       PWR),   # active-low shutdown, pull high = always on
        ("AD",     "GND",        GRY),   # addr = 0x3C
    ]
    for i, (lbl, net, col) in enumerate(left_pins):
        py = uy + 50 + i*40
        draw.line([ux-50, py, ux, py], fill=col, width=2)
        draw.text((ux-54, py), lbl, fill=BLK, anchor="rm")
        draw.text((ux-54, py+13), net, fill=col, anchor="rm")

    # addr annotation
    draw.text((ux-60, uy+248), "addr=0x3C", fill=GRY, anchor="rm")

    # Right pins (LED outputs, 10 shown)
    led_colors_v = [RED,ORG,ORG,GRN,GRN,GRN,GRN,GRN,GRN,GRN]
    for i in range(10):
        py = uy + 30 + i*36
        col = led_colors_v[i]
        net = f"LED_{i+1}"
        draw.line([ux+uw, py, ux+uw+40, py], fill=col, width=2)
        draw.text((ux+uw+44, py), f"OUT{i+1}", fill=BLK, anchor="lm")
        draw.text((ux+uw+44, py+12), net, fill=col, anchor="lm")

    draw.text((ux+uw//2, uy+uh+20), "I2C addr 0x3C  |  /SDB tied HIGH", fill=GRY, anchor="mm")

    # ══════════════════════════════════════════════════
    # R1-R10 + D1-D10 LEDs (right column)
    # ══════════════════════════════════════════════════
    rx0 = 980; dx0 = 1100
    for i in range(10):
        py = uy + 30 + i*36
        col = led_colors_v[i]
        # wire from U1 output
        draw.line([ux+uw+120, py, rx0, py], fill=col, width=2)
        # resistor box
        box(draw, rx0, py-12, 70, 26, f"R{i+1} 33Ω", color=GRY, bg=(248,248,240), lw=1)
        # wire to LED
        draw.line([rx0+70, py, dx0, py], fill=col, width=2)
        # LED symbol (triangle)
        tx, ty = dx0, py
        draw.polygon([(tx,ty-10),(tx,ty+10),(tx+20,ty)], fill=col, outline=BLK)
        draw.line([tx+20,ty-10,tx+20,ty+10], fill=BLK, width=2)
        # label
        draw.text((tx+30, py), f"D{i+1}", fill=BLK, anchor="lm")
        # GND
        draw.line([tx+20, py, tx+60, py], fill=GRY, width=2)
        draw.text((tx+66, py), "GND", fill=GRY, anchor="lm")

    # ══════════════════════════════════════════════════
    # ENC1 — Alps EC11E Encoder (bottom left)
    # ══════════════════════════════════════════════════
    ex, ey, ew, eh = 60, 500, 200, 180
    box(draw, ex, ey, ew, eh, "ENC1", "Alps EC11E15244B3\n15-detent, D-shaft", color=GRN, bg=(235,255,240), lw=2)

    enc_pins = [
        ("A",    "ENC_A",  GRN),
        ("GND",  "GND",    GRY),
        ("B",    "ENC_B",  GRN),
        ("SW_1", "ENC_SW", GRN),
        ("SW_2", "GND",    GRY),
    ]
    for i, (lbl, net, col) in enumerate(enc_pins):
        py = ey + 30 + i*30
        pin_right(draw, ex+ew, py, lbl, net, col)

    # dashed arrow from encoder outputs back to J1
    draw.text((ex+ew+120, ey+eh//2), "→ direct GPIO\nto Daisy via J1", fill=GRN, anchor="lm")

    # ══════════════════════════════════════════════════
    # Legend + BOM summary
    # ══════════════════════════════════════════════════
    lx, ly = 1350, 120
    box(draw, lx, ly, 400, 440, "Bill of Materials", color=BLK, bg=(250,250,245), lw=1)
    bom = [
        ("J1",      "JST-SH SM08B-SRSS-TB 8-pin"),
        ("U1",      "IS31FL3236  (I2C LED driver)"),
        ("ENC1",    "Alps EC11E15244B3  (encoder)"),
        ("D1-D10",  "0805 LED  R/O/G  (×10)"),
        ("R1-R10",  "33Ω 0402  (LED limiters ×10)"),
        ("R11-R12", "4.7kΩ 0402  (I2C pull-ups ×2)"),
        ("C1",      "10µF 0402  (bulk decoupling)"),
        ("C2",      "100nF 0402  (bypass cap)"),
        ("FB1",     "BLM18PG221SN1D  (ferrite bead)"),
        ("",        ""),
        ("Power",   "+3V3 from Daisy Seed"),
        ("Comm",    "I2C: SDA/SCL to Daisy GPIO"),
        ("Encoder", "3 GPIO (A, B, SW) to Daisy"),
        ("Future",  "CAP1188 touch (pad reserved)"),
    ]
    for i, (ref, desc) in enumerate(bom):
        ty = ly + 35 + i*28
        if ref:
            draw.text((lx+14, ty), ref, fill=BLUE, anchor="lm")
            draw.text((lx+120, ty), desc, fill=BLK, anchor="lm")
        else:
            draw.line([lx+10, ty, lx+390, ty], fill=GRY, width=1)

    # footer
    draw.line([40, H-40, W-40, H-40], fill=GRY, width=1)
    draw.text((W//2, H-20), "ICIO500  ·  Faceplate Logic Board  ·  Rev 0.1  ·  Generated by Antigravity",
              fill=GRY, anchor="mm")

    img.save("views/schematic_preview.png", dpi=(150,150))
    print("Saved views/schematic_preview.png")

if __name__ == "__main__":
    main()
