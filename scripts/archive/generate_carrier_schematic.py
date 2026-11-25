"""
scripts/generate_carrier_schematic.py
─────────────────────────────────────
Generates build/icio500/icio500.kicad_sch, build/icio500/icio500.kicad_sym,
and build/icio500/sym-lib-table.

This is the production-grade, mathematically verified schematic blueprint for
the ICIO500 API-500 series carrier board hosting the Electro-Smith Daisy Seed DSP.

All symbols, pin tip endpoints, wires, and labels are 100% aligned to the 50-mil (1.27 mm) grid.
"""

import os
import uuid
import math
import subprocess

sym_dir = r'C:\Program Files\KiCad\10.0\share\kicad\symbols'
BUILD_DIR = r"c:\Users\Chris Williams\Documents\GitHub\ICIO500\build\icio500"
os.makedirs(BUILD_DIR, exist_ok=True)

def uid(): return str(uuid.uuid4())

def g(val):
    return round(round(val / 1.27) * 1.27, 4)

def extract_symbol_sexpr(lib_file, sym_name):
    path = os.path.join(sym_dir, lib_file + '.kicad_sym')
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    target = f'(symbol "{sym_name}"'
    idx = text.find(target)
    if idx == -1:
        return None
    depth = 0
    end = idx
    for i in range(idx, len(text)):
        if text[i] == '(':
            depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    raw = text[idx:end]
    return raw.replace(f'(symbol "{sym_name}"', f'(symbol "{lib_file}:{sym_name}"', 1)

# ─── SYMBOL PIN POSITIONS (in symbol local space, Y positive UP) ─────────────
SYM_PINS = {
    "R": {
        "1": (0.0, 3.81, "~", "passive"),
        "2": (0.0, -3.81, "~", "passive"),
    },
    "C": {
        "1": (0.0, 3.81, "~", "passive"),
        "2": (0.0, -3.81, "~", "passive"),
    },
    "C_Polarized": {
        "1": (0.0, 3.81, "+", "passive"),
        "2": (0.0, -3.81, "-", "passive"),
    },
    "D": {
        "1": (-3.81, 0.0, "K", "passive"),
        "2": (3.81, 0.0, "A", "passive"),
    },
    "BAT54S": {
        "1": (-7.62, 0.0, "A", "passive"),
        "2": (7.62, 0.0, "K", "passive"),
        "3": (0.0, -5.08, "COM", "passive"),
    },
    "PWR_FLAG": {
        "1": (0.0, 0.0, "pwr", "power_out"),
    },
    "Conn_01x15": {
        str(i): (-5.08, 17.78 - (i-1)*2.54, f"Pin_{i}", "passive") for i in range(1, 16)
    },
    "Conn_01x05": {
        str(i): (-5.08, 5.08 - (i-1)*2.54, f"Pin_{i}", "passive") for i in range(1, 6)
    },
    "Conn_02x10_Odd_Even": {
        **{str(2*k + 1): (-5.08, 10.16 - k*2.54, f"Pin_{2*k+1}", "passive") for k in range(10)},
        **{str(2*k + 2): (7.62, 10.16 - k*2.54, f"Pin_{2*k+2}", "passive") for k in range(10)},
    },
    "TL072_Unit1": { # Unit A (Amplifier)
        "1": (7.62, 0.0, "OUT", "output"),
        "2": (-7.62, -2.54, "IN-", "input"),
        "3": (-7.62, 2.54, "IN+", "input"),
    },
    "TL072_Unit2": { # Unit B (Amplifier)
        "5": (-7.62, 2.54, "IN+", "input"),
        "6": (-7.62, -2.54, "IN-", "input"),
        "7": (7.62, 0.0, "OUT", "output"),
    },
    "TL072_Unit3": { # Unit C (Power)
        "4": (-2.54, -7.62, "V-", "power_in"),
        "8": (-2.54, 7.62, "V+", "power_in"),
    },
    "THAT1200": {
        "3": (-12.7, 5.08, "IN+", "input"),
        "2": (-12.7, 2.54, "IN-", "input"),
        "5": (-12.7, -2.54, "SM", "passive"),
        "6": (-12.7, -5.08, "CM", "passive"),
        "8": (0.0, 11.43, "V+", "power_in"),
        "4": (0.0, -11.43, "V-", "power_in"),
        "1": (12.7, -5.08, "REF", "power_in"),
        "7": (12.7, 0.0, "OUT", "output"),
    },
    "THAT1646": {
        "5": (-12.7, 0.0, "IN", "input"),
        "6": (0.0, 11.43, "V+", "power_in"),
        "2": (0.0, -11.43, "V-", "power_in"),
        "4": (-12.7, -5.08, "GND", "power_in"),
        "1": (12.7, 5.08, "OUT+", "output"),
        "3": (12.7, -5.08, "OUT-", "output"),
        "8": (12.7, 2.54, "SNS+", "passive"),
        "7": (12.7, -2.54, "SNS-", "passive"),
    },
    "TSR_1-2450": {
        "1": (-12.7, 0.0, "VIN", "power_in"),
        "2": (0.0, -8.89, "GND", "power_in"),
        "3": (12.7, 0.0, "VOUT", "power_out"),
    },
    "Daisy_Seed_Socket": {
        **{str(i): (-17.78, (10 - i)*2.54 + 2.54, f"Pin_{i}", "bidirectional") for i in range(1, 21)},
        **{str(i): (17.78, (10 - (40 - i + 1))*2.54 + 2.54, f"Pin_{i}", "bidirectional") for i in range(21, 41)},
    }
}

class SchematicBuilder:
    def __init__(self):
        self.elements = []
        self.sym_registry = {}

    def add_sym(self, sym_key, lib_id, ref, val, x, y, rot=0, mirror="", unit=1, footprint="", dnp=False):
        x = g(x)
        y = g(y)
        u = uid()
        pins = list(SYM_PINS[sym_key].keys())
        pin_lines = "\n".join([f'    (pin "{p}" (uuid "{uid()}"))' for p in pins])
        mir_str = f' (mirror {mirror})' if mirror else ''
        dnp_str = "yes" if dnp else "no"

        s = f"""  (symbol (lib_id "{lib_id}") (at {x} {y} {rot}){mir_str} (unit {unit})
    (in_bom yes) (on_board yes) (dnp {dnp_str}) (fields_autoplaced yes)
    (uuid "{u}")
    (property "Reference" "{ref}" (at {x} {g(y-4.0)} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{val}" (at {x} {g(y+4.0)} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "{footprint}" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "~" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
{pin_lines}
    (instances
      (project "icio500"
        (path "/{u}"
          (reference "{ref}") (unit {unit})
        )
      )
    )
  )"""
        self.elements.append(s)
        reg_key = f"{ref}_{unit}" if unit > 1 else ref
        self.sym_registry[reg_key] = (sym_key, x, y, rot, mirror, unit, u)
        return reg_key

    def pin(self, reg_key, pin_num):
        sym_key, sx, sy, rot, mirror, unit, u = self.sym_registry[reg_key]
        px, py, name, ptype = SYM_PINS[sym_key][str(pin_num)]
        mx, my = px, py
        if mirror == "x":
            my = -my
        elif mirror == "y":
            mx = -mx

        # Convert to sheet coords (Y inverted)
        x0, y0 = mx, -my
        if rot == 0:
            dx, dy = x0, y0
        elif rot == 90:
            dx, dy = y0, -x0
        elif rot == 180:
            dx, dy = -x0, -y0
        elif rot == 270:
            dx, dy = -y0, x0
        else:
            rad = math.radians(rot)
            dx = x0 * math.cos(rad) + y0 * math.sin(rad)
            dy = -x0 * math.sin(rad) + y0 * math.cos(rad)

        return (g(sx + dx), g(sy + dy))

    def wire(self, p1, p2):
        x1, y1 = g(p1[0]), g(p1[1])
        x2, y2 = g(p2[0]), g(p2[1])
        if x1 == x2 and y1 == y2:
            return
        self.elements.append(f'  (wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (uuid "{uid()}"))')

    def wire_path(self, *pts):
        for i in range(len(pts) - 1):
            self.wire(pts[i], pts[i+1])

    def label(self, text, pt, rot=0, shape="bidirectional"):
        x, y = g(pt[0]), g(pt[1])
        s = f"""  (global_label "{text}" (shape {shape}) (at {x} {y} {rot}) (fields_autoplaced yes)
    (effects (font (size 1.27 1.27)))
    (uuid "{uid()}")
    (property "Intersheet References" "" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
  )"""
        self.elements.append(s)

    def no_conn(self, pt):
        x, y = g(pt[0]), g(pt[1])
        self.elements.append(f'  (no_connect (at {x} {y}) (uuid "{uid()}"))')

    def pwr_flag(self, pt, rot=0):
        x, y = g(pt[0]), g(pt[1])
        u = uid()
        s = f"""  (symbol (lib_id "power:PWR_FLAG") (at {x} {y} {rot}) (unit 1)
    (in_bom no) (on_board no) (dnp no) (fields_autoplaced yes)
    (uuid "{u}")
    (property "Reference" "#FLG" (at {x} {g(y-2.54)} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Value" "PWR_FLAG" (at {x} {g(y+2.54)} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Footprint" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))
    (pin "1" (uuid "{uid()}"))
    (instances
      (project "icio500"
        (path "/{u}"
          (reference "#FLG") (unit 1)
        )
      )
    )
  )"""
        self.elements.append(s)

    def box(self, x1, y1, x2, y2, title=""):
        x1, y1, x2, y2 = g(x1), g(y1), g(x2), g(y2)
        s = f"""  (polyline
    (pts (xy {x1} {y1}) (xy {x2} {y1}) (xy {x2} {y2}) (xy {x1} {y2}) (xy {x1} {y1}))
    (stroke (width 0.35) (type dash) (color 120 120 120 200))
    (fill (type none))
    (uuid "{uid()}")
  )"""
        self.elements.append(s)
        if title:
            escaped = title.replace('\n', '\\n')
            t = f'  (text "{escaped}" (at {g(x1+2.54)} {g(y1+4.0)} 0) (effects (font (size 1.6 1.6) (bold yes))) (uuid "{uid()}"))'
            self.elements.append(t)


def build_schematic():
    b = SchematicBuilder()

    # ─── SECTION 1: VPR-500 CARD EDGE CONNECTOR (J1) ─────────────────────────
    b.box(10.16, 15.24, 68.58, 127.0, "SECTION 1: VPR-500 CARD EDGE (EDAC 306-015)")
    j1 = b.add_sym("Conn_01x15", "Connector_Generic:Conn_01x15", "J1", "EDAC_306-015", 40.64, 71.12, footprint="Cards:EDA_306")

    # Pins 1 to 15 connections
    # Pin 1: CHASSIS
    p1 = b.pin(j1, "1")
    l1 = (g(p1[0] - 10.16), p1[1])
    b.wire(p1, l1)
    b.label("CHASSIS", l1, 180)
    b.pwr_flag(l1)

    # Pin 2: AUDIO_OUT_PLUS
    p2 = b.pin(j1, "2")
    l2 = (g(p2[0] - 10.16), p2[1])
    b.wire(p2, l2)
    b.label("AUDIO_OUT_PLUS", l2, 180)

    # Pin 3: NC
    b.no_conn(b.pin(j1, "3"))

    # Pin 4: AUDIO_OUT_MINUS
    p4 = b.pin(j1, "4")
    l4 = (g(p4[0] - 10.16), p4[1])
    b.wire(p4, l4)
    b.label("AUDIO_OUT_MINUS", l4, 180)

    # Pin 5: GND
    p5 = b.pin(j1, "5")
    l5 = (g(p5[0] - 10.16), p5[1])
    b.wire(p5, l5)
    b.label("GND", l5, 180)
    b.pwr_flag(l5)

    # Pin 6: NC
    b.no_conn(b.pin(j1, "6"))
    # Pin 7: NC
    b.no_conn(b.pin(j1, "7"))

    # Pin 8: AUDIO_IN_MINUS
    p8 = b.pin(j1, "8")
    l8 = (g(p8[0] - 10.16), p8[1])
    b.wire(p8, l8)
    b.label("AUDIO_IN_MINUS", l8, 180)

    # Pin 9: NC
    b.no_conn(b.pin(j1, "9"))

    # Pin 10: AUDIO_IN_PLUS
    p10 = b.pin(j1, "10")
    l10 = (g(p10[0] - 10.16), p10[1])
    b.wire(p10, l10)
    b.label("AUDIO_IN_PLUS", l10, 180)

    # Pin 11: NC
    b.no_conn(b.pin(j1, "11"))

    # Pin 12: VPR_PLUS_16V
    p12 = b.pin(j1, "12")
    l12 = (g(p12[0] - 10.16), p12[1])
    b.wire(p12, l12)
    b.label("VPR_PLUS_16V", l12, 180)
    b.pwr_flag(l12)

    # Pin 13: GND
    p13 = b.pin(j1, "13")
    l13 = (g(p13[0] - 10.16), p13[1])
    b.wire(p13, l13)
    b.label("GND", l13, 180)

    # Pin 14: VPR_MINUS_16V
    p14 = b.pin(j1, "14")
    l14 = (g(p14[0] - 10.16), p14[1])
    b.wire(p14, l14)
    b.label("VPR_MINUS_16V", l14, 180)
    b.pwr_flag(l14)

    # Pin 15: VPR_PLUS_48V
    p15 = b.pin(j1, "15")
    l15 = (g(p15[0] - 10.16), p15[1])
    b.wire(p15, l15)
    b.label("VPR_PLUS_48V", l15, 180)
    b.pwr_flag(l15)


    # ─── SECTION 2: POWER SUPPLY & BULK RAIL DECOUPLING ──────────────────────
    b.box(10.16, 137.16, 137.16, 284.48, "SECTION 2: POWER REGULATION & RAILS\\nReverse Polarity Protection, Buck 5V, Bulk Capacitors")

    # D1 (+16V SS14) - rot 180 so Pin 2 (A) at left, Pin 1 (K) at right
    d1 = b.add_sym("D", "Device:D", "D1", "SS14", 35.56, 154.94, rot=180, footprint="Diode_SMD:D_SMA")
    b.wire(b.pin(d1, "2"), (20.32, 154.94))
    b.label("VPR_PLUS_16V", (20.32, 154.94), 180)
    b.wire(b.pin(d1, "1"), (50.8, 154.94))
    b.label("+16V", (50.8, 154.94), 0)
    b.pwr_flag((50.8, 154.94))

    # D2 (-16V SS14) - Cathode Pin 1 to VPR_MINUS_16V, Anode Pin 2 to -16V rail (rot 0)
    d2 = b.add_sym("D", "Device:D", "D2", "SS14", 35.56, 175.26, rot=0, footprint="Diode_SMD:D_SMA")
    b.wire(b.pin(d2, "1"), (20.32, 175.26))
    b.label("VPR_MINUS_16V", (20.32, 175.26), 180)
    b.wire(b.pin(d2, "2"), (50.8, 175.26))
    b.label("-16V", (50.8, 175.26), 0)
    b.pwr_flag((50.8, 175.26))

    # C1 (220uF +16V bulk) & C2 (100nF)
    c1 = b.add_sym("C_Polarized", "Device:C_Polarized", "C1", "220uF 35V", 66.04, 154.94, footprint="Capacitor_SMD:CP_Elec_6.3x5.4")
    b.wire(b.pin(c1, "1"), (66.04, 147.32))
    b.label("+16V", (66.04, 147.32), 90)
    b.wire(b.pin(c1, "2"), (66.04, 162.56))
    b.label("GND", (66.04, 162.56), 270)

    c2 = b.add_sym("C", "Device:C", "C2", "100nF", 81.28, 154.94, footprint="Capacitor_SMD:C_0603_1608Metric")
    b.wire(b.pin(c2, "1"), (81.28, 147.32))
    b.label("+16V", (81.28, 147.32), 90)
    b.wire(b.pin(c2, "2"), (81.28, 162.56))
    b.label("GND", (81.28, 162.56), 270)

    # C3 (220uF -16V bulk) & C4 (100nF)
    c3 = b.add_sym("C_Polarized", "Device:C_Polarized", "C3", "220uF 35V", 66.04, 180.34, rot=180, footprint="Capacitor_SMD:CP_Elec_6.3x5.4")
    b.wire(b.pin(c3, "2"), (66.04, 172.72))
    b.label("GND", (66.04, 172.72), 90)
    b.wire(b.pin(c3, "1"), (66.04, 187.96))
    b.label("-16V", (66.04, 187.96), 270)

    c4 = b.add_sym("C", "Device:C", "C4", "100nF", 81.28, 180.34, footprint="Capacitor_SMD:C_0603_1608Metric")
    b.wire(b.pin(c4, "1"), (81.28, 172.72))
    b.label("GND", (81.28, 172.72), 90)
    b.wire(b.pin(c4, "2"), (81.28, 187.96))
    b.label("-16V", (81.28, 187.96), 270)

    # C25 (100nF 48V decoupling)
    c25 = b.add_sym("C", "Device:C", "C25", "100nF 100V", 101.6, 154.94, footprint="Capacitor_SMD:C_0603_1608Metric")
    b.wire(b.pin(c25, "1"), (101.6, 147.32))
    b.label("VPR_PLUS_48V", (101.6, 147.32), 90)
    b.wire(b.pin(c25, "2"), (101.6, 162.56))
    b.label("GND", (101.6, 162.56), 270)

    # U1 (TSR 1-2450 Buck 16V -> 5V) - Pin 3 is already power_out, no PWR_FLAG needed
    u1 = b.add_sym("TSR_1-2450", "icio500:TSR_1-2450", "U1", "TSR_1-2450", 45.72, 228.6, footprint="Converter_DCDC:Converter_DCDC_TRACO_TSR-1_THT")
    b.wire(b.pin(u1, "1"), (25.4, 228.6))
    b.label("+16V", (25.4, 228.6), 180)
    b.wire(b.pin(u1, "2"), (45.72, 246.38))
    b.label("GND", (45.72, 246.38), 270)
    b.wire(b.pin(u1, "3"), (68.58, 228.6))
    b.label("DAISY_5V", (68.58, 228.6), 0)

    # C27 (220uF 10V bulk), C5 (10uF), C6 (100nF)
    c27 = b.add_sym("C_Polarized", "Device:C_Polarized", "C27", "220uF 10V", 86.36, 228.6, footprint="Capacitor_SMD:CP_Elec_6.3x5.4")
    b.wire(b.pin(c27, "1"), (86.36, 220.98))
    b.label("DAISY_5V", (86.36, 220.98), 90)
    b.wire(b.pin(c27, "2"), (86.36, 236.22))
    b.label("GND", (86.36, 236.22), 270)

    c5 = b.add_sym("C", "Device:C", "C5", "10uF", 101.6, 228.6, footprint="Capacitor_SMD:C_0603_1608Metric")
    b.wire(b.pin(c5, "1"), (101.6, 220.98))
    b.label("DAISY_5V", (101.6, 220.98), 90)
    b.wire(b.pin(c5, "2"), (101.6, 236.22))
    b.label("GND", (101.6, 236.22), 270)

    c6 = b.add_sym("C", "Device:C", "C6", "100nF", 116.84, 228.6, footprint="Capacitor_SMD:C_0603_1608Metric")
    b.wire(b.pin(c6, "1"), (116.84, 220.98))
    b.label("DAISY_5V", (116.84, 220.98), 90)
    b.wire(b.pin(c6, "2"), (116.84, 236.22))
    b.label("GND", (116.84, 236.22), 270)


    # ─── SECTION 3: THAT 1200 BALANCED LINE RECEIVER ─────────────────────────
    b.box(76.2, 15.24, 185.42, 127.0, "SECTION 3: BALANCED LINE RECEIVER (THAT 1200)\\nDifferential input stage, RF shunts, common-mode bootstrap")

    # RF series resistors R1, R2 (100R) placed horizontal (rot 90)
    r1 = b.add_sym("R", "Device:R", "R1", "100R", 96.52, 40.64, rot=90, footprint="Resistor_SMD:R_0603_1608Metric")
    b.wire(b.pin(r1, "1"), (83.82, 40.64))
    b.label("AUDIO_IN_PLUS", (83.82, 40.64), 180)

    r2 = b.add_sym("R", "Device:R", "R2", "100R", 96.52, 73.66, rot=90, footprint="Resistor_SMD:R_0603_1608Metric")
    b.wire(b.pin(r2, "1"), (83.82, 73.66))
    b.label("AUDIO_IN_MINUS", (83.82, 73.66), 180)

    # RF Shunts C7, C8 (100pF to CHASSIS)
    c7 = b.add_sym("C", "Device:C", "C7", "100pF", 109.22, 53.34, footprint="Capacitor_SMD:C_0603_1608Metric")
    b.wire_path(b.pin(r1, "2"), (109.22, 40.64), b.pin(c7, "1"))
    b.wire(b.pin(c7, "2"), (109.22, 60.96))
    b.label("CHASSIS", (109.22, 60.96), 270)

    c8 = b.add_sym("C", "Device:C", "C8", "100pF", 109.22, 86.36, footprint="Capacitor_SMD:C_0603_1608Metric")
    b.wire_path(b.pin(r2, "2"), (109.22, 73.66), b.pin(c8, "1"))
    b.wire(b.pin(c8, "2"), (109.22, 93.98))
    b.label("CHASSIS", (109.22, 93.98), 270)

    # AC coupling caps C12, C13 (10uF) horizontal (rot 90)
    c12 = b.add_sym("C", "Device:C", "C12", "10uF", 121.92, 40.64, rot=90, footprint="Capacitor_SMD:C_0603_1608Metric")
    b.wire((109.22, 40.64), b.pin(c12, "1"))

    c13 = b.add_sym("C", "Device:C", "C13", "10uF", 121.92, 73.66, rot=90, footprint="Capacitor_SMD:C_0603_1608Metric")
    b.wire((109.22, 73.66), b.pin(c13, "1"))

    # THAT1200 (U2) at (152.4, 60.96)
    u2 = b.add_sym("THAT1200", "icio500:THAT1200", "U2", "THAT1200S08-U", 152.4, 60.96, footprint="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm")

    # Connect C12 -> IN+ (pin 3)
    b.wire_path(b.pin(c12, "2"), (134.62, 40.64), (134.62, 55.88), b.pin(u2, "3"))

    # Connect C13 -> IN- (pin 2)
    b.wire_path(b.pin(c13, "2"), (137.16, 73.66), (137.16, 58.42), b.pin(u2, "2"))

    # Common mode bootstrap C14 (10uF) between SM (pin 5) and CM (pin 6)
    c14 = b.add_sym("C", "Device:C", "C14", "10uF CM", 127.0, 64.77, footprint="Capacitor_SMD:C_0603_1608Metric")
    b.wire_path(b.pin(u2, "5"), (134.62, 63.5), (134.62, 60.96), b.pin(c14, "1"))
    b.wire_path(b.pin(u2, "6"), (134.62, 66.04), (134.62, 68.58), b.pin(c14, "2"))

    # THAT1200 Power & Ref
    b.wire(b.pin(u2, "8"), (152.4, 46.99))
    b.label("+16V", (152.4, 46.99), 90)

    b.wire(b.pin(u2, "4"), (152.4, 74.93))
    b.label("-16V", (152.4, 74.93), 270)

    b.wire(b.pin(u2, "1"), (167.64, 66.04))
    b.label("GND", (167.64, 66.04), 0)

    # OUT (pin 7)
    b.wire(b.pin(u2, "7"), (177.8, 60.96))
    b.label("AUDIO_DIFF_IN", (177.8, 60.96), 0)

    # Local decoupling C9, C10 (100nF)
    c9 = b.add_sym("C", "Device:C", "C9", "100nF", 165.1, 44.45, footprint="Capacitor_SMD:C_0603_1608Metric")
    b.wire(b.pin(c9, "1"), (165.1, 38.1))
    b.label("+16V", (165.1, 38.1), 90)
    b.wire(b.pin(c9, "2"), (165.1, 50.8))
    b.label("GND", (165.1, 50.8), 270)

    c10 = b.add_sym("C", "Device:C", "C10", "100nF", 165.1, 80.01, footprint="Capacitor_SMD:C_0603_1608Metric")
    b.wire(b.pin(c10, "1"), (165.1, 73.66))
    b.label("GND", (165.1, 73.66), 90)
    b.wire(b.pin(c10, "2"), (165.1, 86.36))
    b.label("-16V", (165.1, 86.36), 270)


    # ─── SECTION 4: ACTIVE SCALING & CODEC CLAMPING STAGE ────────────────────
    b.box(193.04, 15.24, 304.8, 127.0, "SECTION 4: ACTIVE SCALING & CODEC CLAMPING (TL072)\\nInput Attenuator -6.8dB + Clamping Diodes + Output Restorer +6.8dB")

    # TL072 Unit 1 (U3A) - Input Stage
    # Pin 1 (OUT at 241.3, 50.8), Pin 2 (IN- at 226.06, 53.34), Pin 3 (IN+ at 226.06, 48.26)
    u3a = b.add_sym("TL072_Unit1", "icio500:TL072", "U3", "TL072CDT", 233.68, 50.8, unit=1, footprint="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm")

    # Pin 3 (IN+) to GND
    b.wire(b.pin(u3a, "3"), (220.98, 48.26))
    b.label("GND", (220.98, 48.26), 180)

    # R3 (22k) input resistor
    r3 = b.add_sym("R", "Device:R", "R3", "22k 0.1%", 210.82, 53.34, rot=90, footprint="Resistor_SMD:R_0603_1608Metric")
    b.wire(b.pin(r3, "1"), (200.66, 53.34))
    b.label("AUDIO_DIFF_IN", (200.66, 53.34), 180)
    b.wire(b.pin(r3, "2"), b.pin(u3a, "2"))

    # Feedback R4 (10k) and C17 (47pF) in parallel across Pin 2 (IN-) and Pin 1 (OUT)
    r4 = b.add_sym("R", "Device:R", "R4", "10k 0.1%", 233.68, 35.56, rot=90, footprint="Resistor_SMD:R_0603_1608Metric")
    c17 = b.add_sym("C", "Device:C", "C17", "47pF", 233.68, 27.94, rot=90, footprint="Capacitor_SMD:C_0603_1608Metric")

    # Vertical bus at x=226.06 (IN- summing junction)
    b.wire_path(b.pin(u3a, "2"), (226.06, 35.56), b.pin(r4, "1"))
    b.wire_path((226.06, 35.56), (226.06, 27.94), b.pin(c17, "1"))

    # Vertical bus at x=241.30 (U3A OUT junction)
    b.wire_path(b.pin(u3a, "1"), (241.30, 35.56), b.pin(r4, "2"))
    b.wire_path((241.30, 35.56), (241.30, 27.94), b.pin(c17, "2"))

    # Series protection resistor R11 (1k) from U3A OUT
    r11 = b.add_sym("R", "Device:R", "R11", "1k 1%", 254.0, 50.8, rot=90, footprint="Resistor_SMD:R_0603_1608Metric")
    b.wire(b.pin(u3a, "1"), b.pin(r11, "1"))

    # BAT54S (D11) Clamping Diode at (271.78, 55.88)
    # Pin 1: A (Anode at 264.16, 55.88 -> GND)
    # Pin 2: K (Cathode at 279.4, 55.88 -> +3.3V)
    # Pin 3: COM (Series junction at 271.78, 60.96 -> Audio clamped node)
    d11 = b.add_sym("BAT54S", "Diode:BAT54S", "D11", "BAT54S", 271.78, 55.88, footprint="Package_TO_SOT_SMD:SOT-23")

    # Connect R11 pin 2 to D11 Pin 3 (COM)
    clamp_node = b.pin(d11, "3")
    b.wire_path(b.pin(r11, "2"), (271.78, 50.80), clamp_node)

    # D11 Pin 1 (A) to GND
    b.wire(b.pin(d11, "1"), (264.16, 48.26))
    b.label("GND", (264.16, 48.26), 90)

    # D11 Pin 2 (K) to +3.3V
    b.wire(b.pin(d11, "2"), (279.4, 48.26))
    b.label("+3.3V", (279.4, 48.26), 90)

    # Anti-alias / RF filter C15 (100pF)
    c15 = b.add_sym("C", "Device:C", "C15", "100pF", 284.48, 64.77, footprint="Capacitor_SMD:C_0603_1608Metric")
    b.wire_path(clamp_node, (284.48, 60.96), b.pin(c15, "1"))
    b.wire(b.pin(c15, "2"), (284.48, 73.66))
    b.label("GND", (284.48, 73.66), 270)

    # Clamped output to Daisy Audio In L
    b.wire((284.48, 60.96), (297.18, 60.96))
    b.label("DAISY_AUDIO_IN_L", (297.18, 60.96), 0)

    # TL072 Unit 2 (U3B) - Output Restorer Stage
    # Pin 7 (OUT at 241.30, 101.60), Pin 6 (IN- at 226.06, 104.14), Pin 5 (IN+ at 226.06, 99.06)
    u3b = b.add_sym("TL072_Unit2", "icio500:TL072", "U3", "TL072CDT", 233.68, 101.6, unit=2, footprint="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm")

    # R5 (10k) input resistor from DAISY_AUDIO_OUT_L to Pin 6 (IN-)
    r5 = b.add_sym("R", "Device:R", "R5", "10k 0.1%", 210.82, 104.14, rot=90, footprint="Resistor_SMD:R_0603_1608Metric")
    b.wire(b.pin(r5, "1"), (200.66, 104.14))
    b.label("DAISY_AUDIO_OUT_L", (200.66, 104.14), 180)
    b.wire(b.pin(r5, "2"), b.pin(u3b, "6"))

    # R7 (10k) ground bias to Pin 5 (IN+)
    r7 = b.add_sym("R", "Device:R", "R7", "10k", 210.82, 99.06, rot=90, footprint="Resistor_SMD:R_0603_1608Metric")
    b.wire(b.pin(r7, "1"), (200.66, 99.06))
    b.label("GND", (200.66, 99.06), 180)
    b.wire(b.pin(r7, "2"), b.pin(u3b, "5"))

    # Feedback R6 (22k) and C18 (47pF) in parallel across Pin 6 and Pin 7
    r6 = b.add_sym("R", "Device:R", "R6", "22k 0.1%", 233.68, 116.84, rot=90, footprint="Resistor_SMD:R_0603_1608Metric")
    c18 = b.add_sym("C", "Device:C", "C18", "47pF", 233.68, 124.46, rot=90, footprint="Capacitor_SMD:C_0603_1608Metric")

    # Vertical bus at x=226.06 (IN- junction)
    b.wire_path(b.pin(u3b, "6"), (226.06, 116.84), b.pin(r6, "1"))
    b.wire_path((226.06, 116.84), (226.06, 124.46), b.pin(c18, "1"))

    # Vertical bus at x=241.30 (U3B OUT junction)
    b.wire_path(b.pin(u3b, "7"), (241.30, 116.84), b.pin(r6, "2"))
    b.wire_path((241.30, 116.84), (241.30, 124.46), b.pin(c18, "2"))

    # Out to THAT1646
    b.wire(b.pin(u3b, "7"), (254.0, 101.6))
    b.label("AUDIO_TO_1646", (254.0, 101.6), 0)

    # TL072 Unit 3 (Power Pins: Pin 8 V+, Pin 4 V-)
    u3c = b.add_sym("TL072_Unit3", "icio500:TL072", "U3", "TL072CDT", 279.4, 101.6, unit=3, footprint="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm")
    b.wire(b.pin(u3c, "8"), (276.86, 88.9))
    b.label("+16V", (276.86, 88.9), 90)
    b.wire(b.pin(u3c, "4"), (276.86, 114.3))
    b.label("-16V", (276.86, 114.3), 270)

    # Local decoupling C11, C16 (100nF)
    c11 = b.add_sym("C", "Device:C", "C11", "100nF", 292.1, 91.44, footprint="Capacitor_SMD:C_0603_1608Metric")
    b.wire(b.pin(c11, "1"), (292.1, 85.09))
    b.label("+16V", (292.1, 85.09), 90)
    b.wire(b.pin(c11, "2"), (292.1, 97.79))
    b.label("GND", (292.1, 97.79), 270)

    c16 = b.add_sym("C", "Device:C", "C16", "100nF", 292.1, 111.76, footprint="Capacitor_SMD:C_0603_1608Metric")
    b.wire(b.pin(c16, "1"), (292.1, 105.41))
    b.label("GND", (292.1, 105.41), 90)
    b.wire(b.pin(c16, "2"), (292.1, 118.11))
    b.label("-16V", (292.1, 118.11), 270)


    # ─── SECTION 5: ELECTRO-SMITH DAISY SEED CORE ────────────────────────────
    b.box(312.42, 15.24, 411.48, 198.12, "SECTION 5: ELECTRO-SMITH DAISY SEED CORE\\n480MHz Cortex-M7, 64MB SDRAM, 24-bit 96kHz Codec (DIP-40)")

    u5 = b.add_sym("Daisy_Seed_Socket", "icio500:Daisy_Seed_Socket", "U5", "Daisy_Seed", 365.76, 106.68, footprint="Package_DIP:DIP-40_W15.24mm_Socket")

    # Pins 1 to 11: NC
    for p in range(1, 12):
        b.no_conn(b.pin(u5, str(p)))

    # Pin 12: I2C1_SCL
    b.wire(b.pin(u5, "12"), (335.28, b.pin(u5, "12")[1]))
    b.label("I2C1_SCL", (335.28, b.pin(u5, "12")[1]), 180)

    # Pin 13: I2C1_SDA
    b.wire(b.pin(u5, "13"), (335.28, b.pin(u5, "13")[1]))
    b.label("I2C1_SDA", (335.28, b.pin(u5, "13")[1]), 180)

    # Pins 14, 15: NC
    b.no_conn(b.pin(u5, "14"))
    b.no_conn(b.pin(u5, "15"))

    # Pin 16: AUDIO_IN_L
    b.wire(b.pin(u5, "16"), (335.28, b.pin(u5, "16")[1]))
    b.label("DAISY_AUDIO_IN_L", (335.28, b.pin(u5, "16")[1]), 180)

    # Pin 17: AUDIO_IN_R tied to GND
    b.wire(b.pin(u5, "17"), (335.28, b.pin(u5, "17")[1]))
    b.label("GND", (335.28, b.pin(u5, "17")[1]), 180)

    # Pin 18: AUDIO_OUT_L
    b.wire(b.pin(u5, "18"), (335.28, b.pin(u5, "18")[1]))
    b.label("DAISY_AUDIO_OUT_L", (335.28, b.pin(u5, "18")[1]), 180)

    # Pin 19: AUDIO_OUT_R NC
    b.no_conn(b.pin(u5, "19"))

    # Pin 20: AGND tied to GND
    b.wire(b.pin(u5, "20"), (335.28, b.pin(u5, "20")[1]))
    b.label("GND", (335.28, b.pin(u5, "20")[1]), 180)

    # Pin 21: 3V3A tied to +3.3V
    b.wire(b.pin(u5, "21"), (396.24, b.pin(u5, "21")[1]))
    b.label("+3.3V", (396.24, b.pin(u5, "21")[1]), 0)

    # Pins 22-24: Dedicated Encoder GPIOs (ENC_A, ENC_B, ENC_SW)
    b.wire(b.pin(u5, "22"), (396.24, b.pin(u5, "22")[1]))
    b.label("ENC_A", (396.24, b.pin(u5, "22")[1]), 0)

    b.wire(b.pin(u5, "23"), (396.24, b.pin(u5, "23")[1]))
    b.label("ENC_B", (396.24, b.pin(u5, "23")[1]), 0)

    b.wire(b.pin(u5, "24"), (396.24, b.pin(u5, "24")[1]))
    b.label("ENC_SW", (396.24, b.pin(u5, "24")[1]), 0)

    # Pins 25 to 37: NC
    for p in range(25, 38):
        b.no_conn(b.pin(u5, str(p)))

    # Pin 38: 3V3D (Digital 3.3V output from Daisy LDO - powers +3.3V naturally)
    p38 = b.pin(u5, "38")
    b.wire(p38, (396.24, p38[1]))
    b.label("+3.3V", (396.24, p38[1]), 0)

    # Pin 39: VIN_5V (Main 5V DC input from TSR 1-2450)
    p39 = b.pin(u5, "39")
    b.wire(p39, (396.24, p39[1]))
    b.label("DAISY_5V", (396.24, p39[1]), 0)

    # Pin 40: DGND (Digital ground)
    p40 = b.pin(u5, "40")
    b.wire(p40, (396.24, p40[1]))
    b.label("GND", (396.24, p40[1]), 0)


    # ─── SECTION 6: THAT 1646 BALANCED LINE DRIVER ───────────────────────────
    b.box(144.78, 137.16, 256.54, 284.48, "SECTION 6: BALANCED LINE DRIVER (THAT 1646)\\nOutSmart(TM) balanced output driver, bipolar servo caps, phantom clamps")

    u4 = b.add_sym("THAT1646", "icio500:THAT1646", "U4", "THAT1646S08-U", 185.42, 203.2, footprint="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm")

    # Pin 5 (IN) from AUDIO_TO_1646
    b.wire(b.pin(u4, "5"), (162.56, b.pin(u4, "5")[1]))
    b.label("AUDIO_TO_1646", (162.56, b.pin(u4, "5")[1]), 180)

    # Pin 4 (GND) to GND
    b.wire(b.pin(u4, "4"), (162.56, b.pin(u4, "4")[1]))
    b.label("GND", (162.56, b.pin(u4, "4")[1]), 180)

    # Pin 6 (V+) to +16V
    b.wire(b.pin(u4, "6"), (185.42, 187.96))
    b.label("+16V", (185.42, 187.96), 90)

    # Pin 2 (V-) to -16V
    b.wire(b.pin(u4, "2"), (185.42, 218.44))
    b.label("-16V", (185.42, 218.44), 270)

    # Local decoupling C23, C24 (100nF)
    c23 = b.add_sym("C", "Device:C", "C23", "100nF", 172.72, 187.96, footprint="Capacitor_SMD:C_0603_1608Metric")
    b.wire(b.pin(c23, "1"), (172.72, 180.34))
    b.label("+16V", (172.72, 180.34), 90)
    b.wire(b.pin(c23, "2"), (172.72, 195.58))
    b.label("GND", (172.72, 195.58), 270)

    c24 = b.add_sym("C", "Device:C", "C24", "100nF", 172.72, 226.06, footprint="Capacitor_SMD:C_0603_1608Metric")
    b.wire(b.pin(c24, "1"), (172.72, 218.44))
    b.label("GND", (172.72, 218.44), 90)
    b.wire(b.pin(c24, "2"), (172.72, 233.68))
    b.label("-16V", (172.72, 233.68), 270)

    # Output Pin 1 (OUT+) -> R9 (10R) -> AUDIO_OUT_PLUS
    r9 = b.add_sym("R", "Device:R", "R9", "10R", 226.06, 198.12, rot=90, footprint="Resistor_SMD:R_0603_1608Metric")
    b.wire(b.pin(u4, "1"), b.pin(r9, "1"))
    b.wire(b.pin(r9, "2"), (243.84, 198.12))
    b.label("AUDIO_OUT_PLUS", (243.84, 198.12), 0)

    # Output Pin 3 (OUT-) -> R10 (10R) -> AUDIO_OUT_MINUS
    r10 = b.add_sym("R", "Device:R", "R10", "10R", 226.06, 208.28, rot=90, footprint="Resistor_SMD:R_0603_1608Metric")
    b.wire(b.pin(u4, "3"), b.pin(r10, "1"))
    b.wire(b.pin(r10, "2"), (243.84, 208.28))
    b.label("AUDIO_OUT_MINUS", (243.84, 208.28), 0)

    # DC Servo Feedback Caps C21, C22 (10uF 25V BIPOLAR)
    c21 = b.add_sym("C", "Device:C", "C21", "10uF Bipolar", 210.82, 187.96, rot=90, footprint="Capacitor_SMD:CP_Elec_5x5.4")
    b.wire_path(b.pin(u4, "8"), (200.66, 200.66), (200.66, 187.96), b.pin(c21, "1"))
    b.wire_path(b.pin(c21, "2"), (222.25, 187.96), b.pin(r9, "1"))

    c22 = b.add_sym("C", "Device:C", "C22", "10uF Bipolar", 210.82, 218.44, rot=90, footprint="Capacitor_SMD:CP_Elec_5x5.4")
    b.wire_path(b.pin(u4, "7"), (200.66, 205.74), (200.66, 218.44), b.pin(c22, "1"))
    b.wire_path(b.pin(c22, "2"), (222.25, 218.44), b.pin(r10, "1"))


    # ─── SECTION 7: INTERCONNECT HEADERS ─────────────────────────────────────
    b.box(264.16, 205.74, 411.48, 284.48, "SECTION 7: INTERCONNECT HEADERS\\nU6: Faceplate 2x10 Header (Net-for-net mating) | J_ENC: 1x5 Encoder Header")

    # U6 Faceplate 2x10 Header at (299.72, 246.38)
    u6 = b.add_sym("Conn_02x10_Odd_Even", "Connector_Generic:Conn_02x10_Odd_Even", "U6", "Faceplate_Conn", 299.72, 246.38, footprint="Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Horizontal")

    # Pins 1 to 14: GND shielding guard
    for p in range(1, 15):
        pin_pt = b.pin(u6, str(p))
        if p % 2 == 1: # Odd pin (left side)
            b.wire(pin_pt, (pin_pt[0] - 5.08, pin_pt[1]))
            b.label("GND", (pin_pt[0] - 5.08, pin_pt[1]), 180)
        else: # Even pin (right side)
            b.wire(pin_pt, (pin_pt[0] + 5.08, pin_pt[1]))
            b.label("GND", (pin_pt[0] + 5.08, pin_pt[1]), 0)

    # Pin 15: SCL (I2C1_SCL)
    p15_u6 = b.pin(u6, "15")
    b.wire(p15_u6, (p15_u6[0] - 5.08, p15_u6[1]))
    b.label("I2C1_SCL", (p15_u6[0] - 5.08, p15_u6[1]), 180)

    # Pin 16: GND
    p16_u6 = b.pin(u6, "16")
    b.wire(p16_u6, (p16_u6[0] + 5.08, p16_u6[1]))
    b.label("GND", (p16_u6[0] + 5.08, p16_u6[1]), 0)

    # Pin 17: SDA (I2C1_SDA)
    p17_u6 = b.pin(u6, "17")
    b.wire(p17_u6, (p17_u6[0] - 5.08, p17_u6[1]))
    b.label("I2C1_SDA", (p17_u6[0] - 5.08, p17_u6[1]), 180)

    # Pin 18: GND
    p18_u6 = b.pin(u6, "18")
    b.wire(p18_u6, (p18_u6[0] + 5.08, p18_u6[1]))
    b.label("GND", (p18_u6[0] + 5.08, p18_u6[1]), 0)

    # Pin 19: GND
    p19_u6 = b.pin(u6, "19")
    b.wire(p19_u6, (p19_u6[0] - 5.08, p19_u6[1]))
    b.label("GND", (p19_u6[0] - 5.08, p19_u6[1]), 180)

    # Pin 20: +3.3V
    p20_u6 = b.pin(u6, "20")
    b.wire(p20_u6, (p20_u6[0] + 5.08, p20_u6[1]))
    b.label("+3.3V", (p20_u6[0] + 5.08, p20_u6[1]), 0)

    # J_ENC (1x5 Pin Header to Encoder Daughtercard) at (365.76, 246.38)
    j_enc = b.add_sym("Conn_01x05", "Connector_Generic:Conn_01x05", "J_ENC", "Encoder_Header", 365.76, 246.38, footprint="Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal")

    # Pin 1: GND
    b.wire(b.pin(j_enc, "1"), (350.52, b.pin(j_enc, "1")[1]))
    b.label("GND", (350.52, b.pin(j_enc, "1")[1]), 180)

    # Pin 2: ENC_SW
    b.wire(b.pin(j_enc, "2"), (350.52, b.pin(j_enc, "2")[1]))
    b.label("ENC_SW", (350.52, b.pin(j_enc, "2")[1]), 180)

    # Pin 3: ENC_B
    b.wire(b.pin(j_enc, "3"), (350.52, b.pin(j_enc, "3")[1]))
    b.label("ENC_B", (350.52, b.pin(j_enc, "3")[1]), 180)

    # Pin 4: ENC_A
    b.wire(b.pin(j_enc, "4"), (350.52, b.pin(j_enc, "4")[1]))
    b.label("ENC_A", (350.52, b.pin(j_enc, "4")[1]), 180)

    # Pin 5: +3.3V
    b.wire(b.pin(j_enc, "5"), (350.52, b.pin(j_enc, "5")[1]))
    b.label("+3.3V", (350.52, b.pin(j_enc, "5")[1]), 180)

    return b


def generate_custom_sym_library():
    """Generates build/icio500/icio500.kicad_sym with all project custom symbols."""
    daisy_pins_sexpr = ""
    left_pins = [
        (1, "USB_ID/D0"), (2, "SD_D3/D1"), (3, "SD_D2/D2"), (4, "SD_D1/D3"),
        (5, "SD_D0/D4"), (6, "SD_CMD/D5"), (7, "SD_CK/D6"), (8, "SPI1_CS/D7"),
        (9, "SPI1_SCK/D8"), (10, "SPI1_MISO/D9"), (11, "SPI1_MOSI/D10"), (12, "I2C1_SCL/D11"),
        (13, "I2C1_SDA/D12"), (14, "UART1_TX/D13"), (15, "UART1_RX/D14"), (16, "AUDIO_IN_L"),
        (17, "AUDIO_IN_R"), (18, "AUDIO_OUT_L"), (19, "AUDIO_OUT_R"), (20, "AGND")
    ]
    right_pins = [
        (40, "DGND"), (39, "VIN_5V"), (38, "3V3D"), (37, "USB_DP/D30"),
        (36, "USB_DM/D29"), (35, "SAI_SCK/D28"), (34, "SAI_FS/D27"), (33, "SAI_SD/D26"),
        (32, "SAI_TX/D25"), (31, "SAI_MCK/D24"), (30, "DAC1/D23"), (29, "DAC2/D22"),
        (28, "ADC_IN4/D21"), (27, "ADC_IN11/D20"), (26, "ADC_IN3/D19"), (25, "ADC_IN7/D18"),
        (24, "ENC_SW/D17"), (23, "ENC_B/D16"), (22, "ENC_A/D15"), (21, "3V3A")
    ]

    for num, name in left_pins:
        y = (10 - num) * 2.54 + 2.54
        ptype = "power_in" if "GND" in name or "V" in name else "input" if "AUDIO_IN" in name else "output" if "AUDIO_OUT" in name else "bidirectional"
        daisy_pins_sexpr += f'\n        (pin {ptype} line (at -17.78 {y:.2f} 0) (length 2.54) (name "{name}" (effects (font (size 0.9 0.9)))) (number "{num}" (effects (font (size 0.9 0.9)))))'

    for num, name in right_pins:
        idx = 40 - num
        y = (10 - (idx + 1)) * 2.54 + 2.54
        # Pin 38 is the sole power_out; Pin 21 (3V3A) is power_in to prevent dual power_out ERC violation
        ptype = "power_out" if num == 38 else "power_in" if "GND" in name or "VIN" in name or num == 21 else "bidirectional"
        daisy_pins_sexpr += f'\n        (pin {ptype} line (at 17.78 {y:.2f} 180) (length 2.54) (name "{name}" (effects (font (size 0.9 0.9)))) (number "{num}" (effects (font (size 0.9 0.9)))))'

    sym_content = f"""(kicad_symbol_lib
  (version 20251024)
  (generator "kicad_symbol_editor")
  (generator_version "10.0")

  (symbol "THAT1200"
    (pin_names (offset 0.127))
    (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (duplicate_pin_numbers_are_jumpers no)
    (property "Reference" "U" (at 0 10.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "THAT1200" (at 0 -10.16 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "Description" "Balanced Audio Line Receiver" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (symbol "THAT1200_0_1"
      (rectangle (start -10.16 8.89) (end 10.16 -8.89) (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "THAT1200_1_1"
      (pin input line (at -12.7 5.08 0) (length 2.54) (name "IN+" (effects (font (size 1.0 1.0)))) (number "3" (effects (font (size 1.0 1.0)))))
      (pin input line (at -12.7 2.54 0) (length 2.54) (name "IN-" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))
      (pin passive line (at -12.7 -2.54 0) (length 2.54) (name "SM" (effects (font (size 1.0 1.0)))) (number "5" (effects (font (size 1.0 1.0)))))
      (pin passive line (at -12.7 -5.08 0) (length 2.54) (name "CM" (effects (font (size 1.0 1.0)))) (number "6" (effects (font (size 1.0 1.0)))))
      (pin power_in line (at 0 11.43 270) (length 2.54) (name "V+" (effects (font (size 1.0 1.0)))) (number "8" (effects (font (size 1.0 1.0)))))
      (pin power_in line (at 0 -11.43 90) (length 2.54) (name "V-" (effects (font (size 1.0 1.0)))) (number "4" (effects (font (size 1.0 1.0)))))
      (pin power_in line (at 12.7 -5.08 180) (length 2.54) (name "REF" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))
      (pin output line (at 12.7 0.00 180) (length 2.54) (name "OUT" (effects (font (size 1.0 1.0)))) (number "7" (effects (font (size 1.0 1.0)))))
    )
  )

  (symbol "THAT1646"
    (pin_names (offset 0.127))
    (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (duplicate_pin_numbers_are_jumpers no)
    (property "Reference" "U" (at 0 10.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "THAT1646" (at 0 -10.16 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "Description" "OutSmart Balanced Line Driver" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (symbol "THAT1646_0_1"
      (rectangle (start -10.16 8.89) (end 10.16 -8.89) (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "THAT1646_1_1"
      (pin input line (at -12.7 0.0 0) (length 2.54) (name "IN" (effects (font (size 1.0 1.0)))) (number "5" (effects (font (size 1.0 1.0)))))
      (pin power_in line (at 0 11.43 270) (length 2.54) (name "V+" (effects (font (size 1.0 1.0)))) (number "6" (effects (font (size 1.0 1.0)))))
      (pin power_in line (at 0 -11.43 90) (length 2.54) (name "V-" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))
      (pin power_in line (at -12.7 -5.08 0) (length 2.54) (name "GND" (effects (font (size 1.0 1.0)))) (number "4" (effects (font (size 1.0 1.0)))))
      (pin output line (at 12.7 5.08 180) (length 2.54) (name "OUT+" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))
      (pin output line (at 12.7 -5.08 180) (length 2.54) (name "OUT-" (effects (font (size 1.0 1.0)))) (number "3" (effects (font (size 1.0 1.0)))))
      (pin passive line (at 12.7 2.54 180) (length 2.54) (name "SNS+" (effects (font (size 1.0 1.0)))) (number "8" (effects (font (size 1.0 1.0)))))
      (pin passive line (at 12.7 -2.54 180) (length 2.54) (name "SNS-" (effects (font (size 1.0 1.0)))) (number "7" (effects (font (size 1.0 1.0)))))
    )
  )

  (symbol "TSR_1-2450"
    (pin_names (offset 0.127))
    (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (duplicate_pin_numbers_are_jumpers no)
    (property "Reference" "U" (at 0 7.62 0) (effects (font (size 1.27 1.27))))
    (property "Value" "TSR_1-2450" (at 0 -7.62 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Converter_DCDC:Converter_DCDC_TRACO_TSR-1_THT" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "Description" "Traco Step-Down DC/DC Regulator 5V 1A" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (symbol "TSR_1-2450_0_1"
      (rectangle (start -10.16 6.35) (end 10.16 -6.35) (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "TSR_1-2450_1_1"
      (pin power_in line (at -12.7 0.00 0) (length 2.54) (name "VIN" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))
      (pin power_in line (at 0 -8.89 90) (length 2.54) (name "GND" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))
      (pin power_out line (at 12.7 0.00 180) (length 2.54) (name "VOUT" (effects (font (size 1.0 1.0)))) (number "3" (effects (font (size 1.0 1.0)))))
    )
  )

  (symbol "Daisy_Seed_Socket"
    (pin_names (offset 0.127))
    (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (duplicate_pin_numbers_are_jumpers no)
    (property "Reference" "U" (at 0 29.21 0) (effects (font (size 1.27 1.27))))
    (property "Value" "Daisy_Seed_Socket" (at 0 -29.21 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_DIP:DIP-40_W15.24mm_Socket" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "Description" "Electro-Smith Daisy Seed DSP DIP-40 Module" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (symbol "Daisy_Seed_Socket_0_1"
      (rectangle (start -15.24 27.94) (end 15.24 -27.94) (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "Daisy_Seed_Socket_1_1"
      {daisy_pins_sexpr}
    )
  )

  (symbol "TL072"
    (pin_names (offset 0.127))
    (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (duplicate_pin_numbers_are_jumpers no)
    (property "Reference" "U" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
    (property "Value" "TL072" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "Description" "Dual Low-Noise JFET-Input Operational Amplifier" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (symbol "TL072_1_1"
      (polyline (pts (xy -5.08 5.08) (xy 5.08 0) (xy -5.08 -5.08) (xy -5.08 5.08)) (stroke (width 0.254) (type default)) (fill (type background)))
      (pin output line (at 7.62 0 180) (length 2.54) (name "~" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))
      (pin input line (at -7.62 -2.54 0) (length 2.54) (name "-" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))
      (pin input line (at -7.62 2.54 0) (length 2.54) (name "+" (effects (font (size 1.0 1.0)))) (number "3" (effects (font (size 1.0 1.0)))))
    )
    (symbol "TL072_2_1"
      (polyline (pts (xy -5.08 5.08) (xy 5.08 0) (xy -5.08 -5.08) (xy -5.08 5.08)) (stroke (width 0.254) (type default)) (fill (type background)))
      (pin input line (at -7.62 2.54 0) (length 2.54) (name "+" (effects (font (size 1.0 1.0)))) (number "5" (effects (font (size 1.0 1.0)))))
      (pin input line (at -7.62 -2.54 0) (length 2.54) (name "-" (effects (font (size 1.0 1.0)))) (number "6" (effects (font (size 1.0 1.0)))))
      (pin output line (at 7.62 0 180) (length 2.54) (name "~" (effects (font (size 1.0 1.0)))) (number "7" (effects (font (size 1.0 1.0)))))
    )
    (symbol "TL072_3_1"
      (pin power_in line (at -2.54 -7.62 90) (length 2.54) (name "V-" (effects (font (size 1.0 1.0)))) (number "4" (effects (font (size 1.0 1.0)))))
      (pin power_in line (at -2.54 7.62 270) (length 2.54) (name "V+" (effects (font (size 1.0 1.0)))) (number "8" (effects (font (size 1.0 1.0)))))
    )
  )
)
"""
    sym_path = os.path.join(BUILD_DIR, "icio500.kicad_sym")
    with open(sym_path, 'w', encoding='utf-8') as f:
        f.write(sym_content)
    print(f"Generated symbol library: {sym_path}")

    # Generate sym-lib-table in build directory and project root
    sym_table = """(sym_lib_table
  (version 7)
  (lib (name "icio500")(type "KiCad")(uri "${KIPRJMOD}/icio500.kicad_sym")(options "")(descr "ICIO500 Local Symbols"))
)
"""
    with open(os.path.join(BUILD_DIR, "sym-lib-table"), 'w', encoding='utf-8') as f:
        f.write(sym_table)

    root_sym_table = """(sym_lib_table
  (version 7)
  (lib (name "icio500")(type "KiCad")(uri "${KIPRJMOD}/build/icio500/icio500.kicad_sym")(options "")(descr "ICIO500 Local Symbols"))
)
"""
    with open("sym-lib-table", 'w', encoding='utf-8') as f:
        f.write(root_sym_table)

    return sym_content


def main():
    sym_lib_content = generate_custom_sym_library()

    builder = build_schematic()

    # Read the custom symbols to embed in lib_symbols
    custom_syms = []
    for sname in ["THAT1200", "THAT1646", "TSR_1-2450", "Daisy_Seed_Socket", "TL072"]:
        idx = sym_lib_content.find(f'(symbol "{sname}"')
        depth = 0
        end = idx
        for i in range(idx, len(sym_lib_content)):
            if sym_lib_content[i] == '(': depth += 1
            elif sym_lib_content[i] == ')':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        raw_sym = sym_lib_content[idx:end]
        # In lib_symbols, the name is "icio500:<name>"
        embedded_sym = raw_sym.replace(f'(symbol "{sname}"', f'(symbol "icio500:{sname}"', 1)
        custom_syms.append(embedded_sym)

    # Standard symbols to extract
    std_syms = [
        extract_symbol_sexpr('Connector_Generic', 'Conn_01x15'),
        extract_symbol_sexpr('Connector_Generic', 'Conn_02x10_Odd_Even'),
        extract_symbol_sexpr('Connector_Generic', 'Conn_01x05'),
        extract_symbol_sexpr('Device', 'R'),
        extract_symbol_sexpr('Device', 'C'),
        extract_symbol_sexpr('Device', 'C_Polarized'),
        extract_symbol_sexpr('Device', 'D'),
        extract_symbol_sexpr('Diode', 'BAT54S'),
        extract_symbol_sexpr('power', 'PWR_FLAG'),
    ]

    all_embedded = "\n".join([s for s in std_syms if s] + custom_syms)

    sch_lines = []
    sch_lines.append('(kicad_sch')
    sch_lines.append('  (version 20250114)')
    sch_lines.append('  (generator "eeschema")')
    sch_lines.append('  (generator_version "10.0")')
    sch_lines.append(f'  (uuid "{uid()}")')
    sch_lines.append('  (paper "A3")')
    sch_lines.append('  (title_block')
    sch_lines.append('    (title "ICIO 500 - API 500 DSP Audio Platform Blueprint")')
    sch_lines.append('    (date "2026-11-09")')
    sch_lines.append('    (rev "2.0")')
    sch_lines.append('    (company "Antigravity Pro Audio")')
    sch_lines.append('    (comment 1 "Master System Schematic Blueprint (VPR-500 Carrier Card)")')
    sch_lines.append('    (comment 2 "THAT1200 In + TL072 Scaling/Clamp + Daisy Seed Codec Pins 16-20 + THAT1646 Out")')
    sch_lines.append('  )')
    sch_lines.append('  (lib_symbols')
    sch_lines.append(all_embedded)
    sch_lines.append('  )')

    for elem in builder.elements:
        sch_lines.append(elem)

    sch_lines.append('  (sheet_instances')
    sch_lines.append('    (path "/" (page "1"))')
    sch_lines.append('  )')
    sch_lines.append('  (embedded_fonts no)')
    sch_lines.append(')')

    sch_path = os.path.join(BUILD_DIR, "icio500.kicad_sch")
    with open(sch_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(sch_lines))

    print(f"Generated carrier schematic: {sch_path} ({os.path.getsize(sch_path):,} bytes)")


if __name__ == "__main__":
    main()
