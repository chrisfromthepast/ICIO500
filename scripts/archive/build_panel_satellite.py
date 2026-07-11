"""
build_panel_satellite.py
Builds panel_satellite.kicad_pcb – a clean, minimal script.
Run with: & "C:\Program Files\KiCad\10.0\bin\python.exe" scripts/build_panel_satellite.py
"""

import pcbnew
import os

KICAD_FP = r"C:\Program Files\KiCad\10.0\share\kicad\footprints"
OUT      = os.path.join("build", "icio500", "panel_satellite.kicad_pcb")

W, H   = 38.10, 133.35   # board mm
OX, OY = 100.0, 100.0    # KiCad world origin

LED_CX    = 19.05         # LED / window centre X
LED_Y0    = 20.0          # first LED centre Y
LED_PITCH = 8.0
ENC_X     = 19.05
ENC_Y     = 109.35


def mm(v):
    return int(round(v * 1e6))


def pos(x, y):
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))


def fp(lib, name, ref, val, x, y, rot=0):
    p = os.path.join(KICAD_FP, lib + ".pretty")
    f = pcbnew.FootprintLoad(p, name)
    if f is None:
        raise RuntimeError("Missing: " + lib + ":" + name)
    f.SetReference(ref)
    f.SetValue(val)
    f.SetPosition(pos(x, y))
    f.SetOrientationDegrees(rot)
    return f


def net(board, name, _cache={}):
    if (id(board), name) not in _cache:
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        _cache[(id(board), name)] = ni
    return _cache[(id(board), name)]


def apad(footprint, pid, n):
    for pad in footprint.Pads():
        if str(pad.GetNumber()) == str(pid):
            pad.SetNet(n)
            return


def line(board, x1, y1, x2, y2, layer, width_mm):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pos(x1, y1))
    t.SetEnd(pos(x2, y2))
    t.SetWidth(mm(width_mm))
    t.SetLayer(layer)
    board.Add(t)
    return t


def lnet(board, x1, y1, x2, y2, layer, width_mm, n):
    t = line(board, x1, y1, x2, y2, layer, width_mm)
    t.SetNet(n)
    return t


def edge(board, x1, y1, x2, y2):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetStart(pos(x1, y1))
    s.SetEnd(pos(x2, y2))
    s.SetWidth(mm(0.05))
    board.Add(s)


def label(board, text, x, y, size=0.8):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(pos(x, y))
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetLayer(pcbnew.F_SilkS)
    board.Add(t)


# ─────────────────────────────────────────────────────────────────────────────

board = pcbnew.BOARD()
board.SetCopperLayerCount(2)

print("Board outline...")
for seg in [(0,0,W,0),(W,0,W,H),(W,H,0,H),(0,H,0,0)]:
    edge(board, seg[0], seg[1], seg[2], seg[3])

print("Mounting holes...")
for my in (9.5, H - 9.5):
    mh = fp("MountingHole", "MountingHole_3.2mm_M3", "MH", "", W/2, my)
    board.Add(mh)

print("Nets...")
gnd        = net(board, "GND")
pwr        = net(board, "+3V3")
pwr_clean  = net(board, "+3V3_CLEAN")
sda        = net(board, "SDA")
scl        = net(board, "SCL")
enc_a      = net(board, "ENC_A")
enc_b      = net(board, "ENC_B")
enc_sw     = net(board, "ENC_SW")
led_nets   = [net(board, "LED_" + str(i+1))   for i in range(10)]
led_a_nets = [net(board, "LED_" + str(i+1) + "_A") for i in range(10)]

print("J1 – JST connector...")
j1 = fp("Connector_JST", "JST_SH_SM08B-SRSS-TB_1x08-1MP_P1.00mm_Horizontal",
        "J1", "SM08B-SRSS-TB", W/2, 3.5, rot=180)
board.Add(j1)
j1_nets = {1:pwr, 2:gnd, 3:sda, 4:scl, 5:enc_a, 6:enc_b, 7:enc_sw, 8:gnd}
for pnum, n in j1_nets.items():
    apad(j1, pnum, n)

print("FB1 – ferrite bead...")
fb1 = fp("Inductor_SMD", "L_0402_1005Metric", "FB1", "BLM18PG221SN1D", 6, 14, rot=90)
board.Add(fb1)
apad(fb1, "1", pwr)
apad(fb1, "2", pwr_clean)

print("C1 – 10uF...")
c1 = fp("Capacitor_SMD", "C_0402_1005Metric", "C1", "10uF/10V", 12, 14)
board.Add(c1)
apad(c1, "1", pwr_clean)
apad(c1, "2", gnd)

print("C2 – 100nF...")
c2 = fp("Capacitor_SMD", "C_0402_1005Metric", "C2", "100nF", 17, 14)
board.Add(c2)
apad(c2, "1", pwr_clean)
apad(c2, "2", gnd)

print("R11 – SDA pullup...")
r11 = fp("Resistor_SMD", "R_0402_1005Metric", "R11", "4.7k", 25, 14, rot=90)
board.Add(r11)
apad(r11, "1", pwr_clean)
apad(r11, "2", sda)

print("R12 – SCL pullup...")
r12 = fp("Resistor_SMD", "R_0402_1005Metric", "R12", "4.7k", 31, 14, rot=90)
board.Add(r12)
apad(r12, "1", pwr_clean)
apad(r12, "2", scl)

print("U1 – IS31FL3236...")
u1 = fp("Package_SO", "TSSOP-36_6.1x12.5mm_P0.65mm", "U1", "IS31FL3236", 7.5, 56, rot=90)
board.Add(u1)
# Assign key functional nets by pad number (TSSOP-36 IS31FL3236 pinout)
u1_assigns = {
    "9": led_nets[0],  "8": led_nets[1],  "7": led_nets[2],
    "6": led_nets[3],  "5": led_nets[4],  "4": led_nets[5],
    "3": led_nets[6],  "2": led_nets[7],  "1": led_nets[8],
    "19": led_nets[9],
    "10": gnd, "17": gnd, "18": gnd,
    "11": scl,  "12": sda,
    "13": pwr_clean,  # ~SDB high = always enabled
    "14": gnd,        # AD=GND → addr 0x3C
    "15": pwr_clean, "16": pwr_clean,  # VCC
}
for pnum, n in u1_assigns.items():
    apad(u1, pnum, n)

print("R1-R10 – LED resistors...")
for i in range(10):
    ry = LED_Y0 + i * LED_PITCH
    r = fp("Resistor_SMD", "R_0402_1005Metric", "R" + str(i+1), "33R", 14.0, ry, rot=90)
    board.Add(r)
    apad(r, "1", led_nets[i])
    apad(r, "2", led_a_nets[i])

print("D1-D10 – LEDs aligned with faceplate windows...")
colors = ["LED_RED", "LED_ORG", "LED_ORG"] + ["LED_GRN"] * 7
for i in range(10):
    dy = LED_Y0 + i * LED_PITCH
    d = fp("LED_SMD", "LED_0805_2012Metric", "D" + str(i+1), colors[i], LED_CX, dy, rot=90)
    board.Add(d)
    apad(d, "A", led_a_nets[i])
    apad(d, "K", gnd)

print("ENC1 – Alps EC11E...")
enc = fp("Rotary_Encoder", "RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm",
         "ENC1", "EC11E15244B3", ENC_X, ENC_Y, rot=0)
board.Add(enc)
for pnum, n in {1: enc_a, 2: gnd, 3: enc_b, 4: enc_sw, 5: gnd}.items():
    apad(enc, pnum, n)

print("Silkscreen...")
label(board, "ICIO500 Panel Logic v0.1", W/2, H - 3.5, 0.7)
label(board, "J1 -> Daisy",              W/2, 1.2,      0.6)
label(board, "U1 IS31FL3236",            7.5, 42.5,     0.7)
label(board, "EC11E Encoder",            ENC_X, ENC_Y - 15, 0.7)

print("Copper traces – power bus (F.Cu)...")
PW, SW = 0.4, 0.2
# +3V3_CLEAN horizontal bus
lnet(board, 6,12.5, 33,12.5, pcbnew.F_Cu, PW, pwr_clean)
# GND horizontal bus
lnet(board, 4,16.5, 35,16.5, pcbnew.F_Cu, PW, gnd)
# +3V3 from J1 area to FB1
lnet(board, 15.55, 5.5,  6, 5.5, pcbnew.F_Cu, PW, pwr)
lnet(board,  6,    5.5,  6,12.0, pcbnew.F_Cu, PW, pwr)
# SDA
lnet(board, 17.55, 5.5, 17.55, 12.5, pcbnew.F_Cu, SW, sda)
lnet(board, 17.55,12.5,  25,  12.5,  pcbnew.F_Cu, SW, sda)
# SCL
lnet(board, 18.55, 5.5, 18.55, 12.5, pcbnew.F_Cu, SW, scl)
lnet(board, 18.55,12.5,  31,  12.5,  pcbnew.F_Cu, SW, scl)

print("Copper traces – LED rows (F.Cu)...")
for i in range(10):
    ry = LED_Y0 + i * LED_PITCH
    lnet(board, 12.5, ry, 13.5, ry, pcbnew.F_Cu, SW, led_nets[i])
    lnet(board, 14.5, ry, 18.05,ry, pcbnew.F_Cu, SW, led_a_nets[i])

print("Encoder traces (B.Cu)...")
for n, dx in [(enc_a,-3),(enc_b,-5),(enc_sw,-7)]:
    lnet(board, ENC_X+dx, ENC_Y-12, ENC_X+dx, 6, pcbnew.B_Cu, SW, n)
    lnet(board, ENC_X+dx, 6, W/2+dx, 6,           pcbnew.B_Cu, SW, n)

print("GND copper zone (B.Cu)...")
z = pcbnew.ZONE(board)
z.SetLayer(pcbnew.B_Cu)
z.SetNet(gnd)
o = z.Outline()
o.NewOutline()
for x, y in [(0.25,0.25),(W-0.25,0.25),(W-0.25,H-0.25),(0.25,H-0.25)]:
    o.Append(mm(OX+x), mm(OY+y))
z.SetMinThickness(mm(0.25))
board.Add(z)

print("Filling zones...")
try:
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
except Exception as e:
    print("  Zone fill deferred:", e)

print("Saving...")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pcbnew.SaveBoard(OUT, board)
print("DONE ->", OUT)
