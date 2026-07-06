"""
generate_faceplate_schematic.py
───────────────────────────────
Generates build/icio500/faceplate_logic.kicad_sch

Components placed:
  J1   – JST-SH 8-pin (Power + I2C + Encoder lines from Daisy)
  U1   – IS31FL3236  (36-ch I2C LED driver, SOP-36)
  U2   – CAP1188     (8-ch capacitive touch, future, SOIC-16)
  ENC1 – Alps EC11E  (rotary encoder + push switch)
  D1-D10 – 0805 LEDs
  R1-R10 – 33Ω LED current limiters (0402)
  R11,R12 – 4.7kΩ I2C pull-ups (0402)
  C1  – 10µF decoupling (0402)
  C2  – 100nF decoupling (0402)
  FB1 – ferrite bead BLM18 (0402)

Net list:
  +3V3  – power rail from Daisy
  GND   – ground
  SDA   – I2C data
  SCL   – I2C clock
  ENC_A – encoder quadrature A
  ENC_B – encoder quadrature B
  ENC_SW – encoder push switch
  LED_1 … LED_10 – individual LED anode nets
"""

import uuid
import os

# ── helpers ──────────────────────────────────────────────────────────────────

def uid():
    return str(uuid.uuid4())

def prop(name, value, x, y, angle=0, hide=False, bold=False, size=1.27):
    h = "(hide yes)" if hide else ""
    b = "(bold yes)" if bold else ""
    return f"""    (property "{name}" "{value}"
      (at {x} {y} {angle})
      (effects (font (size {size} {size}) {b}) {h})
    )"""

def pin_def(name, number, ptype, at_x, at_y, angle, length=2.54):
    return f'    (pin {ptype} line (at {at_x} {at_y} {angle}) (length {length}) (name "{name}" (effects (font (size 1.016 1.016)))) (number "{number}" (effects (font (size 1.016 1.016)))))'

def symbol_inst(lib_id, ref, value, x, y, angle=0, unit=1, mirror=""):
    mir = f'(mirror {mirror})' if mirror else ''
    return f"""  (symbol
    (lib_id "{lib_id}")
    (at {x} {y} {angle})
    {mir}
    (unit {unit})
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (uuid "{uid()}")
    {prop("Reference", ref, 0, -2.54, bold=True)}
    {prop("Value",     value, 0,  2.54)}
    {prop("Footprint","",0,0,hide=True)}
    {prop("Datasheet","",0,0,hide=True)}
  )"""

def wire(x1, y1, x2, y2):
    return f'  (wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (uuid "{uid()}"))'

def net_label(net, x, y, angle=0):
    return f'  (net_label "{net}" (at {x} {y} {angle}) (fields_autoplaced yes) (uuid "{uid()}") (property "Intersheet References" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes))))'

def power_sym(name, x, y):
    return f"""  (symbol
    (lib_id "power:{name}")
    (at {x} {y} 0)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (uuid "{uid()}")
    {prop("Reference","#PWR",0,-2,hide=True)}
    {prop("Value",name,0,2)}
    {prop("Footprint","",0,0,hide=True)}
    {prop("Datasheet","",0,0,hide=True)}
  )"""

def no_connect(x, y):
    return f'  (no_connect (at {x} {y}) (uuid "{uid()}"))'

# ── lib_symbols section ───────────────────────────────────────────────────────
# We embed minimal symbol definitions for each component so the schematic is
# self-contained and opens correctly without needing every global library.

LIB_SYMBOLS = ""

# ─── JST-SH 8-pin connector ──────────────────────────────────────────────────
def lib_jst():
    pins = ""
    labels = ["3V3", "GND", "SDA", "SCL", "ENC_A", "ENC_B", "ENC_SW", "GND2"]
    for i, lbl in enumerate(labels, 1):
        y = -(i - 1) * 2.54
        pins += f'\n    (pin passive line (at -5.08 {y} 0) (length 2.54) (name "Pin_{i}" (effects (font (size 1.016 1.016)))) (number "{i}" (effects (font (size 1.016 1.016)))))'
    return f"""  (symbol "Local:JST_SH_8"
    (pin_names (offset 1.016))
    (exclude_from_sim no) (in_bom yes) (on_board yes)
    {prop("Reference","J",1.27,1.27,hide=True)}
    {prop("Value","JST_SH_8",1.27,-1.27,hide=True)}
    {prop("Footprint","Connector_JST:JST_SH_SM08B-SRSS-TB_1x08-1MP_P1.00mm_Horizontal",0,0,hide=True)}
    {prop("Datasheet","",0,0,hide=True)}
    (symbol "Local:JST_SH_8_0_1"
      (rectangle (start -2.54 1.27) (end 2.54 {-(len(labels)-1)*2.54 - 1.27}) (stroke (width 0) (type default)) (fill (type background)))
      {pins}
    )
  )"""

# ─── IS31FL3236 LED driver (minimal – just the key pins) ─────────────────────
def lib_is31():
    # Key pins: VCC, GND, SDA, SCL, /SDB, AD, OUT1-OUT10 (we show 10 out of 36)
    pin_list = [
        ("VCC",  "1",  5.08,  8.89, 180),
        ("GND",  "2",  5.08,  6.35, 180),
        ("SDA",  "3",  5.08,  3.81, 180),
        ("SCL",  "4",  5.08,  1.27, 180),
        ("~{SDB}","5", 5.08, -1.27, 180),
        ("AD",   "6",  5.08, -3.81, 180),
    ]
    for i in range(1, 11):
        pin_list.append((f"OUT{i}", str(6+i), -5.08, (i-1)*-2.54 + 8.89, 0))

    pins_str = ""
    for name, num, x, y, ang in pin_list:
        ptype = "power_in" if name in ("VCC","GND") else "bidirectional" if name in ("SDA","SCL") else "output" if name.startswith("OUT") else "input"
        pins_str += f'\n    (pin {ptype} line (at {x} {y} {ang}) (length 2.54) (name "{name}" (effects (font (size 1.016 1.016)))) (number "{num}" (effects (font (size 1.016 1.016)))))'

    return f"""  (symbol "Local:IS31FL3236"
    (pin_names (offset 1.016))
    (exclude_from_sim no) (in_bom yes) (on_board yes)
    {prop("Reference","U",2.54,11.43,hide=True)}
    {prop("Value","IS31FL3236",2.54,-14.0,hide=True)}
    {prop("Footprint","Package_SO:SSOP-36_5.3x10.2mm_P0.65mm",0,0,hide=True)}
    {prop("Datasheet","https://www.issi.com/WW/pdf/IS31FL3236.pdf",0,0,hide=True)}
    (symbol "Local:IS31FL3236_0_1"
      (rectangle (start -3.81 10.16) (end 3.81 -15.24) (stroke (width 0) (type default)) (fill (type background)))
      {pins_str}
    )
  )"""

# ─── Alps EC11E encoder ───────────────────────────────────────────────────────
def lib_ec11():
    pins = [
        ("A",   "1",  5.08,  2.54, 180),
        ("GND", "2",  5.08,  0.0,  180),
        ("B",   "3",  5.08, -2.54, 180),
        ("SW_1","4", -5.08,  2.54,   0),
        ("SW_2","5", -5.08,  0.0,    0),
    ]
    pins_str = ""
    for name, num, x, y, ang in pins:
        ptype = "passive"
        pins_str += f'\n    (pin {ptype} line (at {x} {y} {ang}) (length 2.54) (name "{name}" (effects (font (size 1.016 1.016)))) (number "{num}" (effects (font (size 1.016 1.016)))))'
    return f"""  (symbol "Local:EC11E_Encoder"
    (pin_names (offset 1.016))
    (exclude_from_sim no) (in_bom yes) (on_board yes)
    {prop("Reference","ENC",2.54,3.81,hide=True)}
    {prop("Value","EC11E15244B3",2.54,-3.81,hide=True)}
    {prop("Footprint","Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm",0,0,hide=True)}
    {prop("Datasheet","https://tech.alpsalpine.com/e/products/detail/EC11E15244B3/",0,0,hide=True)}
    (symbol "Local:EC11E_Encoder_0_1"
      (rectangle (start -3.81 3.81) (end 3.81 -3.81) (stroke (width 0) (type default)) (fill (type background)))
      {pins_str}
    )
  )"""

# ─── Generic R, C, LED, Ferrite ───────────────────────────────────────────────
def lib_r():
    return """  (symbol "Local:R"
    (pin_names (offset 0)) (exclude_from_sim no) (in_bom yes) (on_board yes)
    (property "Reference" "R" (at 2.032 0 90) (effects (font (size 1.27 1.27))))
    (property "Value" "R" (at 0 0 90) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Footprint" "Resistor_SMD:R_0402_1005Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "Local:R_0_1"
      (polyline (pts (xy 0 -2.286) (xy 0 -0.762)) (stroke (width 0) (type default)) (fill (type none)))
      (rectangle (start -1.016 -0.762) (end 1.016 0.762) (stroke (width 0) (type default)) (fill (type background)))
      (polyline (pts (xy 0 0.762) (xy 0 2.286)) (stroke (width 0) (type default)) (fill (type none)))
      (pin passive line (at 0 -3.81 90) (length 1.524) (name "~" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 0 3.81 270) (length 1.524) (name "~" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
    )
  )"""

def lib_c():
    return """  (symbol "Local:C"
    (pin_names (offset 0.254)) (exclude_from_sim no) (in_bom yes) (on_board yes)
    (property "Reference" "C" (at 1.778 0 0) (effects (font (size 1.27 1.27))))
    (property "Value" "C" (at 1.778 -2.54 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Footprint" "Capacitor_SMD:C_0402_1005Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "Local:C_0_1"
      (polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.508) (type default)) (fill (type none)))
      (polyline (pts (xy -2.032  0.762) (xy 2.032  0.762)) (stroke (width 0.508) (type default)) (fill (type none)))
      (polyline (pts (xy 0 -0.762) (xy 0 -2.54)) (stroke (width 0) (type default)) (fill (type none)))
      (polyline (pts (xy 0  0.762) (xy 0  2.54)) (stroke (width 0) (type default)) (fill (type none)))
      (pin passive line (at 0  3.81 270) (length 1.27) (name "~" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 0 -3.81 90)  (length 1.27) (name "~" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
    )
  )"""

def lib_led():
    return """  (symbol "Local:LED"
    (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)
    (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
    (property "Value" "LED" (at 0 -2.54 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Footprint" "LED_SMD:LED_0805_2012Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "Local:LED_0_1"
      (polyline (pts (xy -1.27 -1.27) (xy -1.27 1.27) (xy 1.27 0) (xy -1.27 -1.27)) (stroke (width 0) (type default)) (fill (type background)))
      (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27)) (stroke (width 0) (type default)) (fill (type none)))
      (polyline (pts (xy -1.27 0) (xy -2.54 0)) (stroke (width 0) (type default)) (fill (type none)))
      (polyline (pts (xy 1.27 0) (xy 2.54 0)) (stroke (width 0) (type default)) (fill (type none)))
      (pin passive line (at -3.81 0 0) (length 1.27) (name "K" (effects (font (size 1.016 1.016)))) (number "K" (effects (font (size 1.016 1.016)))))
      (pin passive line (at  3.81 0 180) (length 1.27) (name "A" (effects (font (size 1.016 1.016)))) (number "A" (effects (font (size 1.016 1.016)))))
    )
  )"""

def lib_ferrite():
    return """  (symbol "Local:Ferrite_Bead"
    (pin_names (offset 0)) (exclude_from_sim no) (in_bom yes) (on_board yes)
    (property "Reference" "FB" (at 2.032 0 90) (effects (font (size 1.27 1.27))))
    (property "Value" "BLM18PG" (at 0 0 90) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Footprint" "Inductor_SMD:L_0402_1005Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "Local:Ferrite_Bead_0_1"
      (polyline (pts (xy 0 -2.286) (xy 0 -0.762)) (stroke (width 0) (type default)) (fill (type none)))
      (rectangle (start -1.016 -0.762) (end 1.016 0.762) (stroke (width 0.254) (type default)) (fill (type background)))
      (polyline (pts (xy 0 0.762) (xy 0 2.286)) (stroke (width 0) (type default)) (fill (type none)))
      (pin passive line (at 0 -3.81 90) (length 1.524) (name "~" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 0  3.81 270) (length 1.524) (name "~" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
    )
  )"""


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN SCHEMATIC BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

def build():
    lines = []

    # ── Header ──
    lines.append(f"""(kicad_sch
\t(version 20250114)
\t(generator "Antigravity Script")
\t(generator_version "1.0")
\t(uuid "{uid()}")
\t(paper "A3")
\t(title_block
\t\t(title "ICIO500 Faceplate Logic Board")
\t\t(rev "0.1")
\t\t(company "ICIO")
\t)""")

    # ── lib_symbols ──
    lines.append("\t(lib_symbols")
    lines.append(lib_jst())
    lines.append(lib_is31())
    lines.append(lib_ec11())
    lines.append(lib_r())
    lines.append(lib_c())
    lines.append(lib_led())
    lines.append(lib_ferrite())
    lines.append("\t)")   # end lib_symbols

    # ══════════════════════════════════════════════════════════════════════════
    # COMPONENT INSTANCES
    # Layout (all coords in mm on an A3 sheet):
    #   J1  connector:   x=30,  y=50
    #   FB1 ferrite:     x=55,  y=35
    #   C1,C2 decoup:    x=70,  y=35
    #   U1 IS31FL3236:   x=110, y=60
    #   R1-R10 LED res:  x=155, y=20..110 (vertical stack)
    #   D1-D10 LEDs:     x=175, y=20..110
    #   ENC1 encoder:    x=30,  y=130
    #   R11,R12 pullups: x=85,  y=25
    # ══════════════════════════════════════════════════════════════════════════

    # ── J1: JST-SH 8-pin connector ──
    lines.append(f"""  (symbol
    (lib_id "Local:JST_SH_8")
    (at 30 50 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes)
    (uuid "{uid()}")
    {prop("Reference","J1",5,48,bold=True)}
    {prop("Value","SM08B-SRSS-TB",5,52)}
    {prop("Footprint","Connector_JST:JST_SH_SM08B-SRSS-TB_1x08-1MP_P1.00mm_Horizontal",0,0,hide=True)}
    {prop("Datasheet","",0,0,hide=True)}
  )""")

    # ── FB1: Ferrite bead on 3V3 entry ──
    lines.append(f"""  (symbol
    (lib_id "Local:Ferrite_Bead")
    (at 55 35 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes)
    (uuid "{uid()}")
    {prop("Reference","FB1",3,33,bold=True)}
    {prop("Value","BLM18PG221SN1D",3,37)}
    {prop("Footprint","Inductor_SMD:L_0402_1005Metric",0,0,hide=True)}
    {prop("Datasheet","",0,0,hide=True)}
  )""")

    # ── C1: 10µF bulk cap ──
    lines.append(f"""  (symbol
    (lib_id "Local:C")
    (at 68 35 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes)
    (uuid "{uid()}")
    {prop("Reference","C1",3,33,bold=True)}
    {prop("Value","10uF",3,37)}
    {prop("Footprint","Capacitor_SMD:C_0402_1005Metric",0,0,hide=True)}
    {prop("Datasheet","",0,0,hide=True)}
  )""")

    # ── C2: 100nF bypass cap ──
    lines.append(f"""  (symbol
    (lib_id "Local:C")
    (at 78 35 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes)
    (uuid "{uid()}")
    {prop("Reference","C2",3,33,bold=True)}
    {prop("Value","100nF",3,37)}
    {prop("Footprint","Capacitor_SMD:C_0402_1005Metric",0,0,hide=True)}
    {prop("Datasheet","",0,0,hide=True)}
  )""")

    # ── R11: SDA pull-up ──
    lines.append(f"""  (symbol
    (lib_id "Local:R")
    (at 88 25 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes)
    (uuid "{uid()}")
    {prop("Reference","R11",3,23,bold=True)}
    {prop("Value","4.7k",3,27)}
    {prop("Footprint","Resistor_SMD:R_0402_1005Metric",0,0,hide=True)}
    {prop("Datasheet","",0,0,hide=True)}
  )""")

    # ── R12: SCL pull-up ──
    lines.append(f"""  (symbol
    (lib_id "Local:R")
    (at 98 25 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes)
    (uuid "{uid()}")
    {prop("Reference","R12",3,23,bold=True)}
    {prop("Value","4.7k",3,27)}
    {prop("Footprint","Resistor_SMD:R_0402_1005Metric",0,0,hide=True)}
    {prop("Datasheet","",0,0,hide=True)}
  )""")

    # ── U1: IS31FL3236 ──
    lines.append(f"""  (symbol
    (lib_id "Local:IS31FL3236")
    (at 110 60 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes)
    (uuid "{uid()}")
    {prop("Reference","U1",5,45,bold=True)}
    {prop("Value","IS31FL3236",5,75)}
    {prop("Footprint","Package_SO:SSOP-36_5.3x10.2mm_P0.65mm",0,0,hide=True)}
    {prop("Datasheet","https://www.issi.com/WW/pdf/IS31FL3236.pdf",0,0,hide=True)}
  )""")

    # ── ENC1: Alps EC11E encoder ──
    lines.append(f"""  (symbol
    (lib_id "Local:EC11E_Encoder")
    (at 30 130 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes)
    (uuid "{uid()}")
    {prop("Reference","ENC1",5,125,bold=True)}
    {prop("Value","EC11E15244B3",5,135)}
    {prop("Footprint","Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm",0,0,hide=True)}
    {prop("Datasheet","https://tech.alpsalpine.com/e/products/detail/EC11E15244B3/",0,0,hide=True)}
  )""")

    # ── R1-R10: LED current limiters + D1-D10: LEDs ──
    led_colors = ["Red","Orange","Orange","Green","Green","Green","Green","Green","Green","Green"]
    for i in range(10):
        ry = 20 + i * 9
        dy = ry
        rx = 150
        dx = 170

        # Resistor
        lines.append(f"""  (symbol
    (lib_id "Local:R")
    (at {rx} {ry} 90)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes)
    (uuid "{uid()}")
    {prop("Reference",f"R{i+1}",rx-3,ry-2,bold=True)}
    {prop("Value","33R",rx-3,ry+2)}
    {prop("Footprint","Resistor_SMD:R_0402_1005Metric",0,0,hide=True)}
    {prop("Datasheet","",0,0,hide=True)}
  )""")

        # LED
        lines.append(f"""  (symbol
    (lib_id "Local:LED")
    (at {dx} {dy} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes)
    (uuid "{uid()}")
    {prop("Reference",f"D{i+1}",dx,dy-3,bold=True)}
    {prop("Value",led_colors[i],dx,dy+3)}
    {prop("Footprint","LED_SMD:LED_0805_2012Metric",0,0,hide=True)}
    {prop("Datasheet","",0,0,hide=True)}
  )""")

    # ══════════════════════════════════════════════════════════════════════════
    # NET LABELS (key signals – wires are implied by shared label names)
    # ══════════════════════════════════════════════════════════════════════════

    # Power rail labels on connector outputs
    net_positions = [
        ("+3V3", 37, 50),   # J1 pin 1
        ("GND",  37, 52.54),# J1 pin 2
        ("SDA",  37, 55.08),# J1 pin 3
        ("SCL",  37, 57.62),# J1 pin 4
        ("ENC_A", 37, 60.16),
        ("ENC_B", 37, 62.70),
        ("ENC_SW",37, 65.24),
        # U1 inputs
        ("+3V3", 103, 51.11), # VCC
        ("GND",  103, 53.65), # GND
        ("SDA",  103, 56.19), # SDA
        ("SCL",  103, 58.73), # SCL
        # IS31FL3236 addr + shutdown
        ("+3V3", 103, 61.27), # /SDB pulled high = enabled
        ("GND",  103, 63.81), # AD → GND = addr 0x3C
        # I2C pullups top rail
        ("+3V3", 88, 21.19),
        ("+3V3", 98, 21.19),
        ("SDA",  88, 28.81),
        ("SCL",  98, 28.81),
        # Decoupling
        ("+3V3", 68, 31.19),
        ("+3V3", 78, 31.19),
        ("GND",  68, 38.81),
        ("GND",  78, 38.81),
        # Encoder
        ("ENC_A",  37, 127.46),
        ("GND",    37, 130.00),
        ("ENC_B",  37, 132.54),
        ("ENC_SW", 23, 127.46),
        ("GND",    23, 130.00),
        # LED GND cathodes
    ]
    for net, x, y in net_positions:
        lines.append(net_label(net, x, y))

    # GND labels on all LED cathodes
    for i in range(10):
        dy = 20 + i * 9
        lines.append(net_label("GND", 177, dy))

    # OUT1-OUT10 labels connecting IS31FL3236 outputs to resistors
    for i in range(10):
        ry = 20 + i * 9
        lines.append(net_label(f"LED_{i+1}", 143, ry))  # left of resistor
        lines.append(net_label(f"LED_{i+1}", 117, 68.89 - i*2.54))  # U1 OUT pin

    # ══════════════════════════════════════════════════════════════════════════
    # TEXT ANNOTATIONS
    # ══════════════════════════════════════════════════════════════════════════
    lines.append(f'  (text "ICIO500 Faceplate Logic Board\\nFront-panel satellite for Electro-Smith Daisy\\nRev 0.1" (at 15 15 0) (uuid "{uid()}") (effects (font (size 2 2) (bold yes))))')
    lines.append(f'  (text "NOTE: All LEDs are 0805 forward-biased\\nfrom IS31FL3236 constant-current outputs.\\n33R resistors fine-tune brightness." (at 140 5 0) (uuid "{uid()}") (effects (font (size 1.5 1.5))))')
    lines.append(f'  (text "NOTE: ENC_A, ENC_B, ENC_SW route directly\\nto Daisy GPIO via JST connector.\\nDaisy handles quadrature decode in firmware." (at 15 145 0) (uuid "{uid()}") (effects (font (size 1.5 1.5))))')
    lines.append(f'  (text "I2C bus (SDA/SCL)\\nIS31FL3236 addr: 0x3C (AD=GND)\\n4.7k pull-ups to 3V3" (at 78 15 0) (uuid "{uid()}") (effects (font (size 1.5 1.5))))')

    # ── Close ──
    lines.append(")")

    return "\n".join(lines)


if __name__ == "__main__":
    out_path = os.path.join("build", "icio500", "faceplate_logic.kicad_sch")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    content = build()
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Wrote {out_path}  ({len(content):,} bytes)")
