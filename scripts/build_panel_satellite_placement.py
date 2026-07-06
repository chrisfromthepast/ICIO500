"""
build_panel_satellite_placement.py
Places components on the board without assigning nets or drawing tracks,
to bypass the KiCad Python API segfaults.
"""

import pcbnew
import os
import sys

sys.stderr = sys.stdout

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

def edge(board, x1, y1, x2, y2):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetStart(pos(x1, y1))
    s.SetEnd(pos(x2, y2))
    s.SetWidth(mm(0.05))
    board.Add(s)

board = pcbnew.BOARD()

print("Board outline...")
for seg in [(0,0,W,0),(W,0,W,H),(W,H,0,H),(0,H,0,0)]:
    edge(board, seg[0], seg[1], seg[2], seg[3])

print("Mounting holes...")
for my in (9.5, H - 9.5):
    mh = fp("MountingHole", "MountingHole_3.2mm_M3", "MH", "", W/2, my)
    board.Add(mh)

print("J1 – JST connector...")
j1 = fp("Connector_JST", "JST_SH_SM08B-SRSS-TB_1x08-1MP_P1.00mm_Horizontal",
        "J1", "SM08B-SRSS-TB", W/2, 3.5, rot=180)
board.Add(j1)

print("Passives...")
fb1 = fp("Inductor_SMD", "L_0402_1005Metric", "FB1", "BLM18PG", 6, 14, rot=90)
board.Add(fb1)
c1 = fp("Capacitor_SMD", "C_0402_1005Metric", "C1", "10uF", 12, 14)
board.Add(c1)
c2 = fp("Capacitor_SMD", "C_0402_1005Metric", "C2", "100nF", 17, 14)
board.Add(c2)
r11 = fp("Resistor_SMD", "R_0402_1005Metric", "R11", "4.7k", 25, 14, rot=90)
board.Add(r11)
r12 = fp("Resistor_SMD", "R_0402_1005Metric", "R12", "4.7k", 31, 14, rot=90)
board.Add(r12)

print("U1 – IS31FL3236...")
u1 = fp("Package_SO", "TSSOP-36_6.1x12.5mm_P0.65mm", "U1", "IS31FL3236", 7.5, 56, rot=90)
board.Add(u1)

print("R1-R10 and D1-D10...")
for i in range(10):
    ry = LED_Y0 + i * LED_PITCH
    r = fp("Resistor_SMD", "R_0402_1005Metric", "R" + str(i+1), "33R", 14.0, ry, rot=90)
    board.Add(r)
    d = fp("LED_SMD", "LED_0805_2012Metric", "D" + str(i+1), "LED", LED_CX, ry, rot=90)
    board.Add(d)

print("ENC1...")
enc = fp("Rotary_Encoder", "RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm",
         "ENC1", "EC11E", ENC_X, ENC_Y, rot=0)
board.Add(enc)

print("Saving...")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pcbnew.SaveBoard(OUT, board)
print("DONE ->", OUT)
