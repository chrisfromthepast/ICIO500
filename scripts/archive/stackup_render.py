"""
stackup_render.py
-----------------
Generates views/stackup_preview.png – a side-by-side illustration of:
  Left:  the faceplate (front view, as you'd see it in a rack)
  Right: the logic board behind it (back side, LEDs facing forward)
  
All dimensions are taken directly from the KiCad board files so this is
a true 1:1 representation at SCALE px/mm.
"""

from PIL import Image, ImageDraw, ImageFont
import math, os

# ── Physical constants (mm) ──────────────────────────────────────────────────
BOARD_W   = 38.10   # 500-series width
BOARD_H   = 133.35  # 500-series height
KNOB_X    = 19.05   # centre X of encoder shaft
KNOB_Y    = 109.35  # centre Y of encoder shaft (from top)
KNOB_R    = 6.0     # encoder shaft hole radius on faceplate

# LED windows on faceplate (matching fix_windows.py)
LED_W     = 12.0
LED_H     = 4.0
LED_PITCH = 8.0
LED_X0    = KNOB_X - LED_W / 2   # left edge of first window
LED_Y_TOP = 18.0                  # top edge of first window (from top of board)
NUM_LEDS  = 10

# LED colours: top = red, then orange, then green
def led_color(i):
    if i == 0:  return (220, 50,  50,  240)   # red
    if i <= 2:  return (230, 140, 20,  240)   # orange
    return             (50,  220, 80,  240)   # green

# Sacred geometry circle radii (mm)
GEOM_R_OUTER   = 13.5
GEOM_R_INNER   = 9.0
GEOM_R_STAR    = 9.0   # points of the 8-pointed star
GEOM_R_CROSS   = 4.5   # inner crosshair end
TICK_OUTER     = 13.5
TICK_INNER_MAJ = 11.5
TICK_INNER_MIN = 12.5
TICK_COUNT     = 48

SCALE = 8   # pixels per mm   →  38.1mm × 8 = 305px wide,  133.35mm × 8 ≈ 1067px tall

# ── Helper: mm→px ────────────────────────────────────────────────────────────
def px(mm):
    return int(round(mm * SCALE))

BW = px(BOARD_W)
BH = px(BOARD_H)

# ── Colour palette ────────────────────────────────────────────────────────────
COL_BG          = (20,  20,  22)           # very dark app background
COL_FR4_FACE    = (35,  35,  38)           # dark grey FR4 faceplate
COL_FR4_LOGIC   = (20,  35,  30)           # dark green-tinted logic board
COL_COPPER      = (231, 186, 61)           # ENIG gold
COL_SILK        = (220, 220, 220)          # white silkscreen
COL_LABEL       = (180, 180, 180)          # annotation text
COL_SCREW_RING  = (80,  80,  80)
COL_SCREW_SLOT  = (50,  50,  50)
COL_KNOB_BODY   = (25,  25,  25)
COL_KNOB_LINE   = (200, 200, 200)
COL_SHADOW      = (0,   0,   0,   120)

GAP_PX = 40   # horizontal gap between the two boards


# ═══════════════════════════════════════════════════════════════════════════════
# DRAWING HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def draw_rounded_rect(draw, x0, y0, x1, y1, r, fill=None, outline=None, width=1):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill,
                            outline=outline, width=width)

def draw_screw_hole(draw, cx, cy, r_outer=5, r_inner=2):
    draw.ellipse([cx-r_outer, cy-r_outer, cx+r_outer, cy+r_outer],
                 fill=COL_SCREW_RING, outline=(50,50,50), width=1)
    draw.ellipse([cx-r_inner, cy-r_inner, cx+r_inner, cy+r_inner],
                 fill=(10,10,10))
    # slot
    draw.line([cx-r_inner, cy, cx+r_inner, cy], fill=COL_SCREW_SLOT, width=1)

def draw_sacred_geometry(draw, cx, cy):
    """Draw the encoder sacred geometry in gold."""
    def pt(angle_deg, r):
        a = math.radians(angle_deg)
        return (cx + r * math.sin(a), cy - r * math.cos(a))

    r_o = px(GEOM_R_OUTER)
    r_i = px(GEOM_R_INNER)
    r_s = px(GEOM_R_STAR)
    r_c = px(GEOM_R_CROSS)

    # outer circle
    draw.ellipse([cx-r_o, cy-r_o, cx+r_o, cy+r_o],
                 outline=COL_COPPER, width=2)
    # inner circle
    draw.ellipse([cx-r_i, cy-r_i, cx+r_i, cy+r_i],
                 outline=COL_COPPER, width=2)

    # 8-pointed star (two overlapping squares, rotated 0° and 45°)
    for base_angle in (0, 45):
        pts = [pt(base_angle + i*90, r_s) for i in range(4)]
        draw.polygon(pts, outline=COL_COPPER, fill=None, width=2)

    # crosshairs (4 lines, each going from inner to outer radius through centre)
    for angle in (0, 90, 180, 270):
        p1 = pt(angle, r_c)
        p2 = pt(angle, r_o)
        draw.line([p1, p2], fill=COL_COPPER, width=2)

    # 48-tick ring
    for i in range(TICK_COUNT):
        angle = i * 360 / TICK_COUNT
        is_major = (i % 6 == 0)
        r_in = px(TICK_INNER_MAJ if is_major else TICK_INNER_MIN)
        r_out = px(TICK_OUTER)
        p1 = pt(angle, r_in)
        p2 = pt(angle, r_out)
        draw.line([p1, p2], fill=COL_COPPER, width=(2 if is_major else 1))

    # encoder shaft hole (dark circle)
    r_knob = px(KNOB_R * 0.5)
    draw.ellipse([cx-r_knob, cy-r_knob, cx+r_knob, cy+r_knob],
                 fill=COL_KNOB_BODY, outline=COL_COPPER, width=2)


def draw_knob(draw, cx, cy):
    """Draw a physical encoder knob on top of the geometry."""
    R = px(7.5)
    # knob body
    draw.ellipse([cx-R, cy-R, cx+R, cy+R],
                 fill=(30,30,30), outline=(90,90,90), width=3)
    # indicator line
    draw.line([cx, cy, cx, cy - R + 4], fill=COL_KNOB_LINE, width=3)
    # highlight
    draw.arc([cx-R+4, cy-R+4, cx+R-4, cy+R-4], start=-30, end=60,
             fill=(80,80,80), width=2)


# ═══════════════════════════════════════════════════════════════════════════════
# FACEPLATE (LEFT)
# ═══════════════════════════════════════════════════════════════════════════════

def draw_faceplate(draw, ox, oy):
    """Draw the front-panel faceplate at offset (ox, oy)."""
    # Board body
    draw_rounded_rect(draw, ox, oy, ox+BW, oy+BH, r=4,
                      fill=COL_FR4_FACE, outline=(60,60,60), width=2)

    # Screw holes (500-series spec: 9.5mm from top/bottom, centred)
    for yy in (9.5, BOARD_H - 9.5):
        draw_screw_hole(draw, ox + px(KNOB_X), oy + px(yy))

    # LED windows – coloured rectangles with a subtle glow
    for i in range(NUM_LEDS):
        lx = ox + px(LED_X0)
        ly = oy + px(LED_Y_TOP + i * LED_PITCH)
        lx2 = lx + px(LED_W)
        ly2 = ly + px(LED_H)
        col = led_color(i)
        # glow halo
        glow = Image.new('RGBA', (BW + 40, BH + 40), (0,0,0,0))
        gd = ImageDraw.Draw(glow)
        gd.rounded_rectangle(
            [lx - ox + 4, ly - oy + 4, lx2 - ox + 36, ly2 - oy + 36],
            radius=3, fill=(col[0], col[1], col[2], 60)
        )
        # (glow blending skipped to keep deps minimal – just draw the rect)
        draw_rounded_rect(draw, lx, ly, lx2, ly2, r=3,
                          fill=col[:3], outline=(col[0]//2, col[1]//2, col[2]//2), width=1)
        # inner bright spot
        iw = px(LED_W) // 4
        ih = px(LED_H) // 3
        draw.ellipse([lx + px(LED_W)//2 - iw, ly + px(LED_H)//2 - ih,
                      lx + px(LED_W)//2 + iw, ly + px(LED_H)//2 + ih],
                     fill=(min(255, col[0]+60), min(255, col[1]+60), min(255, col[2]+60)))

    # Sacred geometry + knob
    cx = ox + px(KNOB_X)
    cy = oy + px(KNOB_Y)
    draw_sacred_geometry(draw, cx, cy)
    draw_knob(draw, cx, cy)

    # Label
    draw.text((ox + BW//2, oy + BH - 18), "FACEPLATE", fill=COL_LABEL,
              anchor="mm")


# ═══════════════════════════════════════════════════════════════════════════════
# LOGIC BOARD (RIGHT)
# ═══════════════════════════════════════════════════════════════════════════════

def draw_logic_board(draw, ox, oy):
    """Draw the logic board at offset (ox, oy)."""
    # Board body (green-tinted)
    draw_rounded_rect(draw, ox, oy, ox+BW, oy+BH, r=4,
                      fill=COL_FR4_LOGIC, outline=(30,80,50), width=2)

    # Screw holes
    for yy in (9.5, BOARD_H - 9.5):
        draw_screw_hole(draw, ox + px(KNOB_X), oy + px(yy))

    # SMD LED pads – glowing dots where the LEDs sit
    for i in range(NUM_LEDS):
        cx2 = ox + px(KNOB_X)
        cy2 = oy + px(LED_Y_TOP + i * LED_PITCH + LED_H / 2)
        col = led_color(i)
        r_pad = px(1.8)
        # Glow ring
        draw.ellipse([cx2 - r_pad*2, cy2 - r_pad*2, cx2 + r_pad*2, cy2 + r_pad*2],
                     fill=(col[0]//3, col[1]//3, col[2]//3))
        # Pad
        draw.ellipse([cx2 - r_pad, cy2 - r_pad, cx2 + r_pad, cy2 + r_pad],
                     fill=COL_COPPER, outline=(160,130,40), width=1)
        # Silkscreen label
        draw.text((cx2 + r_pad + 4, cy2), f"D{NUM_LEDS - i}", fill=COL_SILK,
                  anchor="lm", font=None)

    # Encoder under-light pad
    cx = ox + px(KNOB_X)
    cy = oy + px(KNOB_Y)
    r_enc = px(3.0)
    draw.ellipse([cx-r_enc, cy-r_enc, cx+r_enc, cy+r_enc],
                 fill=COL_COPPER, outline=(160,130,40), width=2)
    draw.text((cx + r_enc + 4, cy), "ENC_UNDER", fill=COL_SILK, anchor="lm")

    # Encoder footprint outline (dashed square)
    enc_size = px(10)
    for side in range(4):
        x0 = cx - enc_size//2 + (enc_size if side == 1 else 0)
        y0 = cy - enc_size//2 + (enc_size if side == 2 else 0)
        x1 = cx + enc_size//2 - (enc_size if side == 3 else 0)
        y1 = cy + enc_size//2 - (enc_size if side == 0 else 0)
        draw.line([x0, y0, x1, y1], fill=(60,120,80), width=1)

    # Some traces suggestion (horizontal lines)
    for i in range(NUM_LEDS):
        cy2 = oy + px(LED_Y_TOP + i * LED_PITCH + LED_H / 2)
        draw.line([ox + px(KNOB_X) + px(2.5), cy2,
                   ox + BW - 10, cy2],
                  fill=(40, 100, 60), width=1)

    # Label
    draw.text((ox + BW//2, oy + BH - 18), "LOGIC BOARD", fill=COL_LABEL,
              anchor="mm")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    MARGIN = 40
    total_w = MARGIN + BW + GAP_PX + BW + MARGIN
    total_h = MARGIN + BH + MARGIN + 60   # 60px for title bar

    img = Image.new('RGB', (total_w, total_h), COL_BG)
    draw = ImageDraw.Draw(img)

    # Title
    draw.text((total_w // 2, 22), "ICIO500 — PCB STACK-UP MOCKUP",
              fill=(200, 200, 200), anchor="mm")
    draw.line([MARGIN, 38, total_w - MARGIN, 38], fill=(50,50,50), width=1)

    top = 50

    # Left: faceplate
    draw_faceplate(draw, MARGIN, top)

    # Right: logic board
    draw_logic_board(draw, MARGIN + BW + GAP_PX, top)

    # Arrow / connection hint between the two boards
    mid_x = MARGIN + BW + GAP_PX // 2
    mid_y = top + BH // 2
    draw.line([MARGIN + BW + 4, mid_y, MARGIN + BW + GAP_PX - 4, mid_y],
              fill=(80,80,80), width=2)
    draw.polygon([(MARGIN + BW + GAP_PX - 4, mid_y - 5),
                  (MARGIN + BW + GAP_PX - 4, mid_y + 5),
                  (MARGIN + BW + GAP_PX + 2, mid_y)],
                 fill=(80,80,80))
    draw.text((mid_x, mid_y - 12), "1mm gap", fill=(80,80,80), anchor="mm")

    # Column labels
    draw.text((MARGIN + BW//2, top - 14), "FRONT (User sees this)",
              fill=(120,120,120), anchor="mm")
    draw.text((MARGIN + BW + GAP_PX + BW//2, top - 14), "BACK (Logic board)",
              fill=(120,120,120), anchor="mm")

    os.makedirs('views', exist_ok=True)
    out = 'views/stackup_preview.png'
    img.save(out, dpi=(300, 300))
    print(f"Saved {out}  ({total_w}×{total_h}px)")

if __name__ == '__main__':
    main()
