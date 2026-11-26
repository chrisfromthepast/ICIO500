#!/usr/bin/env python3
"""Build kicad/october_surprise.kicad_sch cleanly from KiCad 10 official symbols.

Strictly adheres to AGENTS.md & pcb_hardware_safety.md:
- Never invents IC pinouts from memory; embeds verbatim official KiCad 10 symbols.
- Snaps every symbol origin and wire endpoint onto KiCad's 1.27 mm (50 mil) grid.
- Negative-rail bulk electrolytics (C2, C5) tie Pin 1 (+) -> GND and Pin 2 (-) -> -16V.
- Bipolar clamp on Daisy Audio In uses symmetric 4x antiparallel 1N4148W (never BAT54S to GND).
- 3V3_A (Daisy Pin 21) isolated from 3V3_D (Daisy Pin 38 -> U6.20 faceplate).
- Daisy Pin 22 labeled GPIO_ENC_A_D15 (fixing Rev-1 D14 typo).
"""

import os
import re
import uuid

PROJECT_NAME = "october_surprise"
ROOT_UUID = "a1b2c3d4-0001-4000-8000-000000000001"
SYM_DIR = r"C:\Program Files\KiCad\10.0\share\kicad\symbols"
OUT_SCH = os.path.join("kicad", "october_surprise.kicad_sch")


def U():
    return str(uuid.uuid4())


def snap(val, step=1.27):
    return round(round(val / step) * step, 4)


def G(units_127):
    """Exact multiple of 1.27 mm (50 mil)."""
    return round(units_127 * 1.27, 4)


def extract_sym(lib_file, sym_name):
    txt = open(os.path.join(SYM_DIR, lib_file), encoding="utf-8").read()
    pos = txt.find(f'(symbol "{sym_name}"')
    if pos == -1:
        raise ValueError(f"Symbol {sym_name} not found in {lib_file}")
    depth = 0
    for i in range(pos, len(txt)):
        if txt[i] == "(":
            depth += 1
        elif txt[i] == ")":
            depth -= 1
            if depth == 0:
                return txt[pos : i + 1]
    raise ValueError(f"Unclosed symbol {sym_name}")


def parse_sym_pins(sym_txt):
    """Return {unit_idx: {pin_num: (dx, dy)}} in symbol coordinates (y up)."""
    units = [(m.start(), m.group(1)) for m in re.finditer(r'\(symbol "([^"]+)"', sym_txt)]
    result = {}
    idx = 0
    while True:
        pos = sym_txt.find("(pin ", idx)
        if pos == -1:
            break
        depth = 0
        for i in range(pos, len(sym_txt)):
            if sym_txt[i] == "(":
                depth += 1
            elif sym_txt[i] == ")":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        blk = sym_txt[pos:end]
        idx = end
        unit_name = [u for p, u in units if p < pos][-1]
        m_u = re.search(r"_(\d+)_\d+$", unit_name)
        uidx = int(m_u.group(1)) if m_u else 1
        at = re.search(r"\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\)", blk)
        nb = re.search(r'\(number\s+"([^"]*)"', blk)
        if at and nb:
            result.setdefault(uidx, {})[nb.group(1)] = (float(at.group(1)), float(at.group(2)))
    return result


class SchBuilder:
    def __init__(self):
        self.lib_symbols = []
        self.pin_maps = {}
        self.elements = []
        self.pwr_counter = 1

    def add_lib(self, lib_file, lib_prefix, sym_name):
        s = extract_sym(lib_file, sym_name)
        pins = parse_sym_pins(s)
        full_id = f"{lib_prefix}:{sym_name}"
        s = s.replace(f'(symbol "{sym_name}"', f'(symbol "{full_id}"', 1)
        self.lib_symbols.append(s)
        self.pin_maps[full_id] = pins

    def pin_xy(self, lib_id, x, y, ang, unit, pin_num):
        pm = self.pin_maps[lib_id]
        if unit in pm and pin_num in pm[unit]:
            dx, dy = pm[unit][pin_num]
        elif 0 in pm and pin_num in pm[0]:
            dx, dy = pm[0][pin_num]
        elif 1 in pm and pin_num in pm[1]:
            dx, dy = pm[1][pin_num]
        else:
            raise KeyError(f"Pin {pin_num} not found in {lib_id} unit {unit}")
        a = ang % 360
        if a == 0:
            rx, ry = dx, dy
        elif a == 90:
            rx, ry = -dy, dx
        elif a == 180:
            rx, ry = -dx, -dy
        elif a == 270:
            rx, ry = dy, -dx
        else:
            raise ValueError(f"Unsupported angle {ang}")
        return round(x + rx, 4), round(y - ry, 4)

    def place(
        self,
        lib_id,
        ref,
        value,
        x,
        y,
        ang=0,
        unit=1,
        footprint="",
        lcsc="",
        mpn="",
        vrating="",
        notes="",
        props=None,
        in_bom="yes",
        on_board="yes",
        exclude_from_sim=None,
        ref_off=(0, -3.5),
        val_off=(0, 3.5),
        hide_props=False,
        hide_ref=False,
    ):
        x, y = snap(x), snap(y)
        uid = U()
        extra = f" (exclude_from_sim {exclude_from_sim})" if exclude_from_sim is not None else ""
        rx, ry = round(x + ref_off[0], 3), round(y + ref_off[1], 3)
        vx, vy = round(x + val_off[0], 3), round(y + val_off[1], 3)
        hide_str = " (hide yes)" if hide_props else ""
        hide_ref_str = " (hide yes)" if (hide_props or hide_ref) else ""
        lines = [
            f'  (symbol (lib_id "{lib_id}") (at {x} {y} {ang}) (unit {unit}){extra}',
            f'    (in_bom {in_bom}) (on_board {on_board}) (dnp no) (uuid "{uid}")',
            f'    (property "Reference" "{ref}" (at {rx} {ry} 0) (effects (font (size 1.1 1.1)){hide_ref_str}))',
            f'    (property "Value" "{value}" (at {vx} {vy} 0) (effects (font (size 1.1 1.1)){hide_str}))',
            f'    (property "Footprint" "{footprint}" (at {x} {y} 0) (effects (font (size 1.0 1.0)) (hide yes)))',
        ]
        if lcsc:
            lines.append(f'    (property "LCSC" "{lcsc}" (at {x} {y} 0) (effects (font (size 1.0 1.0)) (hide yes)))')
        if mpn:
            lines.append(f'    (property "MPN" "{mpn}" (at {x} {y} 0) (effects (font (size 1.0 1.0)) (hide yes)))')
        if vrating:
            lines.append(f'    (property "VoltageRating" "{vrating}" (at {x} {y} 0) (effects (font (size 1.0 1.0)) (hide yes)))')
        if notes:
            lines.append(f'    (property "Notes" "{notes}" (at {x} {y} 0) (effects (font (size 1.0 1.0)) (hide yes)))')
        if props:
            for k, v in props.items():
                lines.append(f'    (property "{k}" "{v}" (at {x} {y} 0) (effects (font (size 1.0 1.0)) (hide yes)))')
        lines.append(f'    (instances (project "{PROJECT_NAME}" (path "/{ROOT_UUID}" (reference "{ref}") (unit {unit}))))')
        lines.append("  )")
        self.elements.append("\n".join(lines))
        return {
            p: self.pin_xy(lib_id, x, y, ang, unit, p)
            for p in (list(self.pin_maps[lib_id].get(unit, {}).keys()) + list(self.pin_maps[lib_id].get(0, {}).keys()))
        }

    def pwr(self, rail_name, x, y, ang=0, pwr_flag=False):
        """Place stock GND/+5V power symbol or clean global_label for custom rails."""
        x, y = snap(x), snap(y)
        if rail_name in ("GND", "+5V"):
            ref = f"#PWR{self.pwr_counter:03d}"
            self.pwr_counter += 1
            pins = self.place(
                f"power:{rail_name}",
                ref,
                rail_name,
                x,
                y,
                ang=ang,
                unit=1,
                in_bom="no",
                on_board="no",
                ref_off=(0, -2.5),
                val_off=(0, 3.0 if ang == 0 else -3.0),
                hide_ref=True,
            )
            pt = pins["1"]
        else:
            # Determine label orientation so text reads nicely away from wire
            lang = 90 if ang in (0, 90) else 270
            if ang == 180:
                lang = 180
            self.glabel(rail_name, (x, y), ang=lang, shape="bidirectional")
            pt = (x, y)

        if pwr_flag:
            fref = f"#FLG{self.pwr_counter:03d}"
            self.pwr_counter += 1
            fx, fy = round(x + 2.54, 4), round(y - 2.54, 4)
            fpins = self.place(
                "power:PWR_FLAG",
                fref,
                "PWR_FLAG",
                fx,
                fy,
                ang=0,
                unit=1,
                in_bom="no",
                on_board="no",
                hide_props=True,
            )
            self.ortho_wire(pt, fpins["1"], horiz_first=False)
        return pt

    def wire(self, p1, p2):
        x1, y1 = snap(p1[0]), snap(p1[1])
        x2, y2 = snap(p2[0]), snap(p2[1])
        if abs(x1 - x2) < 1e-4 and abs(y1 - y2) < 1e-4:
            return
        self.elements.append(
            f'  (wire (pts (xy {x1:.4f} {y1:.4f}) (xy {x2:.4f} {y2:.4f}))\n'
            f'    (stroke (width 0) (type default))\n'
            f'    (uuid "{U()}")\n  )'
        )

    def ortho_wire(self, p1, p2, mid_x=None, horiz_first=True):
        p1 = (snap(p1[0]), snap(p1[1]))
        p2 = (snap(p2[0]), snap(p2[1]))
        if abs(p1[0] - p2[0]) < 1e-4 or abs(p1[1] - p2[1]) < 1e-4:
            self.wire(p1, p2)
            return
        if mid_x is not None:
            mx = snap(mid_x)
            self.wire(p1, (mx, p1[1]))
            self.wire((mx, p1[1]), (mx, p2[1]))
            self.wire((mx, p2[1]), p2)
        elif horiz_first:
            m = (p2[0], p1[1])
            self.wire(p1, m)
            self.wire(m, p2)
        else:
            m = (p1[0], p2[1])
            self.wire(p1, m)
            self.wire(m, p2)

    def junction(self, p):
        self.elements.append(
            f'  (junction (at {snap(p[0]):.4f} {snap(p[1]):.4f}) (diameter 0) (color 0 0 0 0)\n    (uuid "{U()}")\n  )'
        )

    def nc(self, p):
        self.elements.append(f'  (no_connect (at {snap(p[0]):.4f} {snap(p[1]):.4f}) (uuid "{U()}"))')

    def glabel(self, name, p, ang=0, shape="bidirectional"):
        just = " (justify right)" if ang == 180 else (" (justify left)" if ang == 0 else "")
        self.elements.append(
            f'  (global_label "{name}" (shape {shape}) (at {snap(p[0]):.4f} {snap(p[1]):.4f} {ang})\n'
            f'    (effects (font (size 1.0 1.0)){just})\n    (uuid "{U()}")\n  )'
        )

    def text(self, s, x, y, size=1.7, bold="yes"):
        esc = s.replace('"', '\\"')
        self.elements.append(
            f'  (text "{esc}" (exclude_from_sim no) (at {x} {y} 0)\n'
            f'    (effects (font (size {size} {size}) (bold {bold})) (justify left))\n    (uuid "{U()}")\n  )'
        )

    def box(self, x1, y1, x2, y2):
        self.elements.append(
            f'  (rectangle (start {x1} {y1}) (end {x2} {y2})\n'
            f'    (stroke (width 0.25) (type dash)) (fill (type none))\n    (uuid "{U()}")\n  )'
        )


def build():
    b = SchBuilder()

    # Official verbatim symbols (zero `extends`, zero custom power symbols)
    b.add_lib("Amplifier_Operational.kicad_sym", "Amplifier_Operational", "LM2904")
    b.add_lib("Converter_DCDC.kicad_sym", "Converter_DCDC", "TSR_1-2450")
    b.add_lib("Device.kicad_sym", "Device", "D")
    b.add_lib("Device.kicad_sym", "Device", "D_Schottky")
    b.add_lib("Device.kicad_sym", "Device", "D_TVS")
    b.add_lib("Device.kicad_sym", "Device", "L")
    b.add_lib("Device.kicad_sym", "Device", "FerriteBead")
    b.add_lib("Device.kicad_sym", "Device", "R")
    b.add_lib("Device.kicad_sym", "Device", "C")
    b.add_lib("Device.kicad_sym", "Device", "C_Polarized")
    b.add_lib("Connector_Generic.kicad_sym", "Connector_Generic", "Conn_01x05")
    b.add_lib("Connector_Generic.kicad_sym", "Connector_Generic", "Conn_01x15")
    b.add_lib("Connector_Generic.kicad_sym", "Connector_Generic", "Conn_01x20")
    b.add_lib("Connector_Generic.kicad_sym", "Connector_Generic", "Conn_02x10_Odd_Even")
    b.add_lib("power.kicad_sym", "power", "+5V")
    b.add_lib("power.kicad_sym", "power", "GND")
    b.add_lib("power.kicad_sym", "power", "PWR_FLAG")
    b.add_lib("Mechanical.kicad_sym", "Mechanical", "MountingHole")

    SP_R = {"Sim.Device": "R", "Sim.Pins": "1=1 2=2"}
    SP_C = {"Sim.Device": "C", "Sim.Pins": "1=1 2=2"}
    SP_D1N4148 = {"Sim.Library": "spice_models/diodes.lib", "Sim.Name": "D1N4148", "Sim.Device": "D", "Sim.Pins": "1=2 2=1"}
    SP_DBAV21W = {"Sim.Library": "spice_models/diodes.lib", "Sim.Name": "DBAV21W", "Sim.Device": "D", "Sim.Pins": "1=2 2=1"}
    SP_DSS14 = {"Sim.Library": "spice_models/diodes.lib", "Sim.Name": "DSS14", "Sim.Device": "D", "Sim.Pins": "1=2 2=1"}
    SP_TVS18 = {"Sim.Library": "spice_models/diodes.lib", "Sim.Name": "TVS_SMBJ18CA", "Sim.Device": "SUBCKT", "Sim.Pins": "1=1 2=2"}
    SP_L22U = {"Sim.Library": "spice_models/diodes.lib", "Sim.Name": "L_SWPA_22U", "Sim.Device": "SUBCKT", "Sim.Pins": "1=1 2=2"}
    SP_L10U = {"Sim.Library": "spice_models/diodes.lib", "Sim.Name": "L_ANR_10U", "Sim.Device": "SUBCKT", "Sim.Pins": "1=1 2=2"}
    SP_FB600 = {"Sim.Library": "spice_models/diodes.lib", "Sim.Name": "FB_600R_100M", "Sim.Device": "SUBCKT", "Sim.Pins": "1=1 2=2"}
    SP_TSR = {"Sim.Library": "spice_models/diodes.lib", "Sim.Name": "TSR1_2450", "Sim.Device": "SUBCKT", "Sim.Pins": "1=1 2=2 3=3"}
    SP_OPA = {"Sim.Library": "spice_models/OPA1656_DUAL.lib", "Sim.Name": "OPA1656_DUAL", "Sim.Device": "SUBCKT", "Sim.Pins": "1=1 2=2 3=3 4=4 5=5 6=6 7=7 8=8"}

    R0603 = "Resistor_SMD:R_0603_1608Metric"
    R1206 = "Resistor_SMD:R_1206_3216Metric"
    C0603 = "Capacitor_SMD:C_0603_1608Metric"
    C0805 = "Capacitor_SMD:C_0805_2012Metric"
    C1206 = "Capacitor_SMD:C_1206_3216Metric"
    CP8X10 = "Capacitor_SMD:CP_Elec_8x10.5"
    DSMB = "Diode_SMD:D_SMB"
    L4020 = "Inductor_SMD:L_Sunlord_SWPA4020S"
    L4018 = "Inductor_SMD:L_APV_ANR4018"
    L0805 = "Inductor_SMD:L_0805_2012Metric"
    FILM5 = "Capacitor_THT:C_Rect_L7.2mm_W4.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2"
    SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
    DIP8_SOCK = "Package_DIP:DIP-8_W7.62mm_Socket"

    def wire_vert(comp, x_val, y_top, y_bot):
        p1, p2 = comp["1"], comp["2"]
        top_p, bot_p = (p1, p2) if p1[1] < p2[1] else (p2, p1)
        b.wire((x_val, y_top), top_p)
        b.wire(bot_p, (x_val, y_bot))

    # =========================================================================
    # ZONE 1: VPR-500 EDGE, TVS, PASSIVE LOW-NOISE LC+FB RAILS & BUCK ISOLATION
    # =========================================================================
    b.box(14, 16, 174, 128)
    b.text("1. POWER: VPR-500 EDGE, TVS, PASSIVE LC+FB PI-FILTERS & TSR-1 BUCK ISOLATION", 16.5, 20.5)

    j1 = b.place(
        "Connector_Generic:Conn_01x15", "J1", "VPR500_Edge_15P", G(30), G(48),
        footprint="Cards:EDA_306", exclude_from_sim="yes", mpn="306-015-520-102",
        notes="15-pin .156 VPR-500 card edge", ref_off=(-8, -23), val_off=(8, -23),
    )
    j1_nets = {
        "1": ("CHASSIS_GND", "passive"),
        "2": ("OUT_P", "input"),
        "4": ("OUT_N", "input"),
        "5": ("GND", None),
        "8": ("IN_N", "output"),
        "10": ("IN_P", "output"),
        "12": ("+16V_RAW", "output"),
        "13": ("GND", None),
        "14": ("-16V_RAW", "output"),
    }
    for pno in [str(i) for i in range(1, 16)]:
        pt = j1[pno]
        if pno in j1_nets:
            nname, shape = j1_nets[pno]
            stub = (pt[0] - G(6), pt[1])
            b.wire(pt, stub)
            if nname == "GND":
                ang_g = 90 if pno == "13" else 0
                dx_g = -G(2) if pno == "13" else 0
                dy_g = G(2) if pno == "5" else 0
                g = b.pwr("GND", stub[0] + dx_g, stub[1] + dy_g, ang=ang_g)
                b.ortho_wire(stub, g, horiz_first=False)
            else:
                b.glabel(nname, stub, ang=180, shape=shape)
        else:
            b.nc(pt)

    # Mounting Holes MH1, MH2 & Chassis Ground Star Bleed (R27 10R + C23 100nF)
    b.place("Mechanical:MountingHole", "MH1", "M3_Mount", G(20), G(82), ang=0, footprint="MountingHole:MountingHole_3.2mm_M3", in_bom="no", exclude_from_sim="yes", ref_off=(-3, -3), val_off=(3, 3))
    b.place("Mechanical:MountingHole", "MH2", "M3_Mount", G(32), G(82), ang=0, footprint="MountingHole:MountingHole_3.2mm_M3", in_bom="no", exclude_from_sim="yes", ref_off=(-3, -3), val_off=(3, 3))
    b.glabel("CHASSIS_GND", (G(20), G(93)), ang=180, shape="passive")
    r27 = b.place("Device:R", "R27", "10", G(26), G(93), ang=90, footprint=R0603, lcsc="C22859", mpn="0603WAF100JT5E", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    c23 = b.place("Device:C", "C23", "100nF", G(35), G(93), ang=90, footprint=C0603, lcsc="C14663", mpn="CC0603KRX7R9BB104", vrating="50V", props=SP_C, ref_off=(0, -3), val_off=(0, 3))
    b.wire((G(20), G(93)), r27["2"])
    b.wire(r27["1"], c23["2"])
    b.wire(c23["1"], b.pwr("GND", G(41), G(93), ang=0))

    # --- TIER 1 (TOP): ISOLATED +5V DAISY SEED BUCK FEEDER ---
    # +16V_BUS -> L1 (22uH) -> +16V_BUCK -> U1 (TSR 1-2450) -> +5V_BUCK -> L2 (10uH) -> +5V_FILT -> FB3 (600R) -> +5V
    y5_top, y5_mid, y5_gnd = G(26), G(33), G(40)
    b.wire(b.pwr("+16V_BUS", G(46), G(22), ang=0), (G(46), y5_top))
    l1 = b.place("Device:L", "L1", "22uH", G(52), y5_top, ang=90, footprint=L4020, lcsc="C82401", mpn="SWPA4020S220MT", vrating="1.05A", props=SP_L22U, ref_off=(0, -3.5), val_off=(0, 3.0))
    b.wire((G(46), y5_top), l1["2"])
    u1 = b.place("Converter_DCDC:TSR_1-2450", "U1", "TSR_1-2450", G(80), G(28), ang=0, footprint="Converter_DCDC:Converter_DCDC_TRACO_TSR-1_THT", lcsc="C53183920", mpn="TSR 1-2450", vrating="36V", props=SP_TSR, ref_off=(0, -6.5), val_off=(0, 7.5))
    b.wire(l1["1"], u1["1"])
    b.wire(b.pwr("+16V_BUCK", G(64), G(22), ang=0, pwr_flag=True), (G(64), y5_top))
    b.junction((G(60), y5_top)); b.junction((G(64), y5_top)); b.junction((G(68), y5_top))
    c30 = b.place("Device:C", "C30", "10uF", G(60), y5_mid, ang=0, footprint=C1206, lcsc="C76666", mpn="C3216X7R1V106KT000E", vrating="35V", props=SP_C, ref_off=(-4.5, -1), val_off=(-4.5, 1.8))
    c4 = b.place("Device:C_Polarized", "C4", "220uF", G(68), y5_mid, ang=0, footprint=CP8X10, lcsc="C970697", mpn="RVT1V221M0810", vrating="35V", props=SP_C, ref_off=(-5, -1), val_off=(-5, 1.8))
    wire_vert(c30, G(60), y5_top, y5_gnd)
    wire_vert(c4, G(68), y5_top, y5_gnd)
    b.wire(u1["2"], (G(80), y5_gnd))

    # U1.3 (+5V_BUCK) -> C3 (220uF) + C31 (10uF) + C33 (100nF) [230.1uF < 470uF limit] -> L2 (10uH) -> +5V_FILT + C32 -> FB3 -> +5V
    l2 = b.place("Device:L", "L2", "10uH", G(110), y5_top, ang=90, footprint=L4018, lcsc="C6808084", mpn="ANR4018T100M", vrating="1.2A", props=SP_L10U, ref_off=(0, -3.5), val_off=(0, 3.0))
    b.wire(u1["3"], l2["2"])
    b.wire(b.pwr("+5V_BUCK", G(90), G(22), ang=0), (G(90), y5_top))
    b.junction((G(90), y5_top)); b.junction((G(97), y5_top)); b.junction((G(103), y5_top))
    c3 = b.place("Device:C_Polarized", "C3", "220uF", G(90), y5_mid, ang=0, footprint=CP8X10, lcsc="C970697", mpn="RVT1V221M0810", vrating="35V", props=SP_C, ref_off=(-5, -1), val_off=(-5, 1.8))
    c31 = b.place("Device:C", "C31", "10uF", G(97), y5_mid, ang=0, footprint=C1206, lcsc="C76666", mpn="C3216X7R1V106KT000E", vrating="35V", props=SP_C, ref_off=(-4.5, -1), val_off=(-4.5, 1.8))
    c33 = b.place("Device:C", "C33", "100nF", G(103), y5_mid, ang=0, footprint=C0603, lcsc="C14663", mpn="CC0603KRX7R9BB104", vrating="50V", props=SP_C, ref_off=(-4.5, -1), val_off=(-4.5, 1.8))
    wire_vert(c3, G(90), y5_top, y5_gnd)
    wire_vert(c31, G(97), y5_top, y5_gnd)
    wire_vert(c33, G(103), y5_top, y5_gnd)

    fb3 = b.place("Device:FerriteBead", "FB3", "600R", G(123), y5_top, ang=90, footprint=L0805, lcsc="C1017", mpn="GZ2012D601TF", vrating="500mA", props=SP_FB600, ref_off=(0, -3.5), val_off=(0, 3.0))
    b.wire(l2["1"], fb3["2"])
    b.wire(b.pwr("+5V_FILT", G(116), G(22), ang=0, pwr_flag=True), (G(116), y5_top))
    b.junction((G(116), y5_top))
    c32 = b.place("Device:C", "C32", "10uF", G(116), y5_mid, ang=0, footprint=C1206, lcsc="C76666", mpn="C3216X7R1V106KT000E", vrating="35V", props=SP_C, ref_off=(-4.5, -1), val_off=(-4.5, 1.8))
    wire_vert(c32, G(116), y5_top, y5_gnd)
    b.wire(fb3["1"], b.pwr("+5V", G(131), y5_top, ang=0, pwr_flag=True))

    # Shared Tier-1 GND bus
    b.wire((G(60), y5_gnd), (G(116), y5_gnd))
    for jx in [68, 80, 90, 97, 103]:
        b.junction((G(jx), y5_gnd))
    b.wire((G(80), y5_gnd), b.pwr("GND", G(80), G(44), ang=0, pwr_flag=True))

    # --- TIER 2 (MIDDLE): +16V ENTRY, TVS CLAMP & ANALOG AUDIO PI-FILTER ---
    yp_top, yp_mid, yp_gnd = G(54), G(61), G(68)
    b.glabel("+16V_RAW", (G(46), yp_top), ang=180, shape="input")
    d1 = b.place("Device:D_Schottky", "D1", "SS14", G(53), yp_top, ang=180, footprint="Diode_SMD:D_SMA", lcsc="C2480", mpn="SS14", vrating="40V", props=SP_DSS14, ref_off=(0, -3), val_off=(0, 3))
    b.wire((G(46), yp_top), d1["2"])
    l3 = b.place("Device:L", "L3", "10uH", G(82), yp_top, ang=90, footprint=L4018, lcsc="C6808084", mpn="ANR4018T100M", vrating="1.2A", props=SP_L10U, ref_off=(0, -3.5), val_off=(0, 3.0))
    b.wire(d1["1"], l3["2"])
    b.wire(b.pwr("+16V_BUS", G(61), G(50), ang=0, pwr_flag=True), (G(61), yp_top))
    b.junction((G(61), yp_top)); b.junction((G(63), yp_top)); b.junction((G(71), yp_top))
    d19 = b.place("Device:D_TVS", "D19", "SMBJ18CA", G(63), yp_mid, ang=90, footprint=DSMB, lcsc="C78413", mpn="SMBJ18CA", vrating="18Vrwm/29.2Vc", props=SP_TVS18, ref_off=(-5, -1), val_off=(-5, 1.8))
    c1 = b.place("Device:C_Polarized", "C1", "220uF", G(71), yp_mid, ang=0, footprint=CP8X10, lcsc="C970697", mpn="RVT1V221M0810", vrating="35V", props=SP_C, ref_off=(-5, -1), val_off=(-5, 1.8))
    wire_vert(d19, G(63), yp_top, yp_gnd)
    wire_vert(c1, G(71), yp_top, yp_gnd)

    fb1 = b.place("Device:FerriteBead", "FB1", "600R", G(101), yp_top, ang=90, footprint=L0805, lcsc="C1017", mpn="GZ2012D601TF", vrating="500mA", props=SP_FB600, ref_off=(0, -3.5), val_off=(0, 3.0))
    b.wire(l3["1"], fb1["2"])
    b.wire(b.pwr("+16V_FILT", G(91), G(50), ang=0, pwr_flag=True), (G(91), yp_top))
    b.junction((G(91), yp_top))
    c34 = b.place("Device:C", "C34", "10uF", G(91), yp_mid, ang=0, footprint=C1206, lcsc="C76666", mpn="C3216X7R1V106KT000E", vrating="35V", props=SP_C, ref_off=(-4.5, -1), val_off=(-4.5, 1.8))
    wire_vert(c34, G(91), yp_top, yp_gnd)

    b.wire(fb1["1"], (G(131), yp_top))
    b.wire(b.pwr("+16V", G(131), G(50), ang=0, pwr_flag=True), (G(131), yp_top))
    b.junction((G(110), yp_top)); b.junction((G(120), yp_top))
    c36 = b.place("Device:C_Polarized", "C36", "220uF", G(110), yp_mid, ang=0, footprint=CP8X10, lcsc="C970697", mpn="RVT1V221M0810", vrating="35V", props=SP_C, ref_off=(-5, -1), val_off=(-5, 1.8))
    c35 = b.place("Device:C", "C35", "10uF", G(120), yp_mid, ang=0, footprint=C1206, lcsc="C76666", mpn="C3216X7R1V106KT000E", vrating="35V", props=SP_C, ref_off=(-4.5, -1), val_off=(-4.5, 1.8))
    wire_vert(c36, G(110), yp_top, yp_gnd)
    wire_vert(c35, G(120), yp_top, yp_gnd)

    b.wire((G(63), yp_gnd), (G(120), yp_gnd))
    for jx in [71, 91, 110]:
        b.junction((G(jx), yp_gnd))

    # --- TIER 3 (BOTTOM): -16V ENTRY, TVS CLAMP & ANALOG AUDIO PI-FILTER ---
    # Signed polarity rule: GND (0V) on TOP (Pin 1 +), -16V (-16V) on BOTTOM (Pin 2 -)
    ym_gnd, ym_mid, ym_bot = G(78), G(84), G(90)
    b.wire((G(91), yp_gnd), (G(91), ym_gnd))
    b.junction((G(91), ym_gnd))
    b.glabel("-16V_RAW", (G(46), ym_bot), ang=180, shape="input")
    d2 = b.place("Device:D_Schottky", "D2", "SS14", G(53), ym_bot, ang=0, footprint="Diode_SMD:D_SMA", lcsc="C2480", mpn="SS14", vrating="40V", props=SP_DSS14, ref_off=(0, -3), val_off=(0, 3))
    b.wire((G(46), ym_bot), d2["1"])  # Pin 1 (K) <- -16V_RAW
    l4 = b.place("Device:L", "L4", "10uH", G(82), ym_bot, ang=90, footprint=L4018, lcsc="C6808084", mpn="ANR4018T100M", vrating="1.2A", props=SP_L10U, ref_off=(0, -3.5), val_off=(0, 3.0))
    b.wire(d2["2"], l4["2"])          # Pin 2 (A) -> -16V_BUS
    b.wire(b.pwr("-16V_BUS", G(61), G(95), ang=270, pwr_flag=True), (G(61), ym_bot))
    b.junction((G(61), ym_bot)); b.junction((G(63), ym_bot)); b.junction((G(71), ym_bot))
    d20 = b.place("Device:D_TVS", "D20", "SMBJ18CA", G(63), ym_mid, ang=90, footprint=DSMB, lcsc="C78413", mpn="SMBJ18CA", vrating="18Vrwm/29.2Vc", props=SP_TVS18, ref_off=(-5, -1), val_off=(-5, 1.8))
    c2 = b.place("Device:C_Polarized", "C2", "220uF", G(71), ym_mid, ang=0, footprint=CP8X10, lcsc="C970697", mpn="RVT1V221M0810", vrating="35V", props=SP_C, notes="Neg rail: Pad 1 (+)->GND, Pad 2 (-)->-16V_BUS", ref_off=(-5, -1), val_off=(-5, 1.8))
    wire_vert(d20, G(63), ym_gnd, ym_bot)
    b.wire((G(71), ym_gnd), c2["1"])  # Pin 1 (+) -> GND
    b.wire(c2["2"], (G(71), ym_bot))  # Pin 2 (-) -> -16V_BUS

    fb2 = b.place("Device:FerriteBead", "FB2", "600R", G(101), ym_bot, ang=90, footprint=L0805, lcsc="C1017", mpn="GZ2012D601TF", vrating="500mA", props=SP_FB600, ref_off=(0, -3.5), val_off=(0, 3.0))
    b.wire(l4["1"], fb2["2"])
    b.wire(b.pwr("-16V_FILT", G(91), G(95), ang=270, pwr_flag=True), (G(91), ym_bot))
    b.junction((G(91), ym_bot))
    c37 = b.place("Device:C", "C37", "10uF", G(91), ym_mid, ang=0, footprint=C1206, lcsc="C76666", mpn="C3216X7R1V106KT000E", vrating="35V", props=SP_C, ref_off=(-4.5, -1), val_off=(-4.5, 1.8))
    wire_vert(c37, G(91), ym_gnd, ym_bot)

    b.wire(fb2["1"], (G(131), ym_bot))
    b.wire(b.pwr("-16V", G(131), G(95), ang=270, pwr_flag=True), (G(131), ym_bot))
    b.junction((G(110), ym_bot)); b.junction((G(120), ym_bot))
    c5 = b.place("Device:C_Polarized", "C5", "220uF", G(110), ym_mid, ang=0, footprint=CP8X10, lcsc="C970697", mpn="RVT1V221M0810", vrating="35V", props=SP_C, notes="Neg rail: Pad 1 (+)->GND, Pad 2 (-)->-16V", ref_off=(-5, -1), val_off=(-5, 1.8))
    c38 = b.place("Device:C", "C38", "10uF", G(120), ym_mid, ang=0, footprint=C1206, lcsc="C76666", mpn="C3216X7R1V106KT000E", vrating="35V", props=SP_C, ref_off=(-4.5, -1), val_off=(-4.5, 1.8))
    b.wire((G(110), ym_gnd), c5["1"])  # Pin 1 (+) -> GND
    b.wire(c5["2"], (G(110), ym_bot))  # Pin 2 (-) -> -16V
    wire_vert(c38, G(120), ym_gnd, ym_bot)

    b.wire((G(57), ym_gnd), (G(120), ym_gnd))
    b.pwr("GND", G(57), ym_gnd, ang=90)
    b.junction((G(63), ym_gnd))
    for jx in [71, 91, 110]:
        b.junction((G(jx), ym_gnd))

    # =========================================================================
    # ZONE 2: INPUT RF FILTER, 100V FILM COUPLING, 3-OP-AMP INA & SYMMETRIC CLAMP
    # =========================================================================
    b.box(178, 16, 406, 128)
    b.text("2. INPUT RF FILTER (100V), 100V FILM COUPLING, BAV21W +48V CLAMP & SOCKETED U2 (-16.5dB, 0 DEG)", 180.5, 21)

    y_ip, y_in = G(36), G(70)
    b.glabel("IN_P", (G(148), y_ip), ang=180, shape="input")
    b.glabel("IN_N", (G(148), y_in), ang=180, shape="input")

    r1 = b.place("Device:R", "R1", "100", G(156), y_ip, ang=90, footprint=R1206, lcsc="C319961", mpn="AR06BTCV1000", vrating="200V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    r2 = b.place("Device:R", "R2", "100", G(156), y_in, ang=90, footprint=R1206, lcsc="C319961", mpn="AR06BTCV1000", vrating="200V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    b.wire((G(148), y_ip), r1["2"])
    b.wire((G(148), y_in), r2["2"])

    x_rf1, x_rf2 = G(162), G(168)
    b.wire(r1["1"], (x_rf2, y_ip)); b.junction((x_rf1, y_ip)); b.junction((x_rf2, y_ip))
    b.wire(r2["1"], (x_rf2, y_in)); b.junction((x_rf1, y_in)); b.junction((x_rf2, y_in))

    c10 = b.place("Device:C", "C10", "220pF", x_rf1, y_ip + G(8), ang=0, footprint=C0805, lcsc="C113819", mpn="CC0805JRNPO0BN221", vrating="100V", props=SP_C, ref_off=(-4.5, 0), val_off=(4.5, 0))
    b.wire((x_rf1, y_ip), c10["1"]); b.wire(c10["2"], b.pwr("GND", x_rf1, y_ip + G(13), ang=0))
    c11 = b.place("Device:C", "C11", "220pF", x_rf1, y_in + G(8), ang=0, footprint=C0805, lcsc="C113819", mpn="CC0805JRNPO0BN221", vrating="100V", props=SP_C, ref_off=(-4.5, 0), val_off=(4.5, 0))
    b.wire((x_rf1, y_in), c11["1"]); b.wire(c11["2"], b.pwr("GND", x_rf1, y_in + G(13), ang=0))
    c14 = b.place("Device:C", "C14", "100pF", x_rf2, G(53), ang=0, footprint=C0603, lcsc="C107033", mpn="CC0603JRNPO0BN101", vrating="100V", props=SP_C, ref_off=(-4.5, 0), val_off=(4.5, 0))
    b.wire((x_rf2, y_ip), c14["1"]); b.wire(c14["2"], (x_rf2, y_in))

    c12 = b.place("Device:C", "C12", "1uF", G(176), y_ip, ang=90, footprint=FILM5, lcsc="C2840662", mpn="MEB105J100V82CL0035", vrating="100V", props=SP_C, ref_off=(0, -3), val_off=(0, 3))
    c13 = b.place("Device:C", "C13", "1uF", G(176), y_in, ang=90, footprint=FILM5, lcsc="C2840662", mpn="MEB105J100V82CL0035", vrating="100V", props=SP_C, ref_off=(0, -3), val_off=(0, 3))
    b.wire((x_rf2, y_ip), c12["2"])
    b.wire((x_rf2, y_in), c13["2"])

    x_bias, x_cl = G(184), G(190)
    b.wire(c12["1"], (G(196), y_ip)); b.junction((x_bias, y_ip)); b.junction((x_cl, y_ip))
    b.wire(c13["1"], (G(196), y_in)); b.junction((x_bias, y_in)); b.junction((x_cl, y_in))

    r3 = b.place("Device:R", "R3", "100k", x_bias, y_ip + G(8), ang=0, footprint=R0603, lcsc="C122538", mpn="RT0603BRD07100KL", vrating="75V", props=SP_R, ref_off=(-4.5, 0), val_off=(4.5, 0))
    b.wire((x_bias, y_ip), r3["1"]); b.wire(r3["2"], b.pwr("GND", x_bias, y_ip + G(13), ang=0))
    r4 = b.place("Device:R", "R4", "100k", x_bias, y_in + G(8), ang=0, footprint=R0603, lcsc="C122538", mpn="RT0603BRD07100KL", vrating="75V", props=SP_R, ref_off=(-4.5, 0), val_off=(4.5, 0))
    b.wire((x_bias, y_in), r4["1"]); b.wire(r4["2"], b.pwr("GND", x_bias, y_in + G(13), ang=0))

    d3 = b.place("Device:D", "D3", "BAV21W", x_cl, y_ip - G(5), ang=270, footprint="Diode_SMD:D_SOD-123", lcsc="C113947", mpn="BAV21W", vrating="250V", props=SP_DBAV21W, ref_off=(-4.5, 0), val_off=(4.5, 0))
    d4 = b.place("Device:D", "D4", "BAV21W", x_cl, y_ip + G(5), ang=270, footprint="Diode_SMD:D_SOD-123", lcsc="C113947", mpn="BAV21W", vrating="250V", props=SP_DBAV21W, ref_off=(-4.5, 0), val_off=(4.5, 0))
    b.wire(b.pwr("+16V", x_cl, y_ip - G(10), ang=0), d3["1"])
    b.wire(d3["2"], (x_cl, y_ip)); b.wire((x_cl, y_ip), d4["1"])
    b.wire(d4["2"], b.pwr("-16V", x_cl, y_ip + G(10), ang=270))

    d5 = b.place("Device:D", "D5", "BAV21W", x_cl, y_in - G(5), ang=270, footprint="Diode_SMD:D_SOD-123", lcsc="C113947", mpn="BAV21W", vrating="250V", props=SP_DBAV21W, ref_off=(-4.5, 0), val_off=(4.5, 0))
    d6 = b.place("Device:D", "D6", "BAV21W", x_cl, y_in + G(5), ang=270, footprint="Diode_SMD:D_SOD-123", lcsc="C113947", mpn="BAV21W", vrating="250V", props=SP_DBAV21W, ref_off=(-4.5, 0), val_off=(4.5, 0))
    b.wire(b.pwr("+16V", x_cl, y_in - G(10), ang=0), d5["1"])
    b.wire(d5["2"], (x_cl, y_in)); b.wire((x_cl, y_in), d6["1"])
    b.wire(d6["2"], b.pwr("-16V", x_cl, y_in + G(10), ang=270))

    # Stoppers R28, R29 (1k) -> Socketed U2A, U2B buffers
    r28 = b.place("Device:R", "R28", "1k", G(200), y_ip, ang=90, footprint=R0603, lcsc="C110776", mpn="RT0603BRD071KL", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    r29 = b.place("Device:R", "R29", "1k", G(200), y_in, ang=90, footprint=R0603, lcsc="C110776", mpn="RT0603BRD071KL", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    b.wire((G(196), y_ip), r28["2"]); b.wire((G(196), y_in), r29["2"])

    u2_notes = "Machined DIP-8 socket C2874007 (IC254V-12-08-0743): install OPA1656IDR on SOIC8-to-DIP8 adapter or dual DIP-8 op-amp"
    u2a = b.place("Amplifier_Operational:LM2904", "U2", "OPA1656", G(212), G(38), ang=0, unit=1, footprint=DIP8_SOCK, lcsc="C2874007", mpn="OPA1656_ON_DIP8_SOCKET", vrating="36V", notes=u2_notes, props=SP_OPA, ref_off=(-2, -7), val_off=(4, 7))
    u2b = b.place("Amplifier_Operational:LM2904", "U2", "OPA1656", G(212), G(72), ang=0, unit=2, footprint=DIP8_SOCK, lcsc="C2874007", mpn="OPA1656_ON_DIP8_SOCKET", vrating="36V", notes=u2_notes, props=SP_OPA, ref_off=(-2, -7), val_off=(4, 7))
    b.wire(r28["1"], u2a["3"]); b.wire(r29["1"], u2b["5"])
    # Clean unity feedback loops on U2A and U2B (no deleted elements!)
    b.wire(u2a["2"], (G(204), u2a["2"][1])); b.wire((G(204), u2a["2"][1]), (G(204), G(45))); b.wire((G(204), G(45)), (G(220), G(45))); b.wire((G(220), G(45)), u2a["1"]); b.junction(u2a["1"])
    b.wire(u2b["6"], (G(204), u2b["6"][1])); b.wire((G(204), u2b["6"][1]), (G(204), G(79))); b.wire((G(204), G(79)), (G(220), G(79))); b.wire((G(220), G(79)), u2b["7"]); b.junction(u2b["7"])

    # U3A Diff Amp (G = +1.5k / 10k = +0.1500x, 0 deg)
    u3a = b.place("Amplifier_Operational:LM2904", "U3", "OPA1656", G(248), G(54), ang=0, unit=1, footprint=SOIC8, lcsc="C1849431", mpn="OPA1656IDR", vrating="36V", props=SP_OPA, ref_off=(-2, -7), val_off=(4, 7))
    r5 = b.place("Device:R", "R5", "10k", G(228), G(40), ang=90, footprint=R0603, lcsc="C95204", mpn="RT0603BRD0710KL", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    r7 = b.place("Device:R", "R7", "10k", G(228), G(68), ang=90, footprint=R0603, lcsc="C95204", mpn="RT0603BRD0710KL", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    b.ortho_wire(u2a["1"], r5["2"], horiz_first=False)
    b.ortho_wire(u2b["7"], r7["2"], horiz_first=False)
    b.ortho_wire(r5["1"], u3a["3"], mid_x=G(236))
    b.ortho_wire(r7["1"], u3a["2"], mid_x=G(236))
    b.junction(u3a["3"]); b.junction(u3a["2"])

    # R6 (1.5k) + C15 (220pF) on U3A.+ to GND (staggered taps avoid 4-way junction)
    r6 = b.place("Device:R", "R6", "1.5k", G(234), G(33), ang=0, footprint=R0603, lcsc="C705741", mpn="RT0603BRD071K5L", vrating="75V", props=SP_R, ref_off=(-4.5, 0), val_off=(4.5, 0))
    c15 = b.place("Device:C", "C15", "220pF", G(242), G(33), ang=0, footprint=C0603, lcsc="C27675", mpn="CL10C221JB8NNNC", vrating="50V", props=SP_C, ref_off=(-4.5, 0), val_off=(4.5, 0))
    b.wire((G(234), G(40)), r6["2"]); b.junction((G(234), G(40)))
    b.wire(r6["1"], (G(234), G(26))); b.wire((G(234), G(26)), (G(242), G(26)))
    b.wire((G(238), G(26)), b.pwr("GND", G(238), G(23), ang=180)); b.junction((G(238), G(26)))
    b.wire((G(242), G(26)), c15["1"]); b.wire(c15["2"], (G(242), G(40))); b.wire((G(242), G(40)), (G(234), G(40)))

    # R8 (1.5k) + C16 (220pF) feedback around U3A
    r8 = b.place("Device:R", "R8", "1.5k", G(248), G(66), ang=90, footprint=R0603, lcsc="C705741", mpn="RT0603BRD071K5L", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    c16 = b.place("Device:C", "C16", "220pF", G(248), G(74), ang=90, footprint=C0603, lcsc="C27675", mpn="CL10C221JB8NNNC", vrating="50V", props=SP_C, ref_off=(0, -3), val_off=(0, 3))
    b.wire(u3a["2"], (G(238), u3a["2"][1])); b.wire((G(238), u3a["2"][1]), (G(238), G(74))); b.wire((G(238), G(74)), c16["2"]); b.wire((G(238), G(66)), r8["2"]); b.junction((G(238), G(66)))
    b.wire(r8["1"], (G(258), G(66))); b.wire(c16["1"], (G(258), G(74))); b.wire((G(258), G(74)), (G(258), G(66))); b.junction((G(258), G(66)))
    b.wire((G(258), G(66)), (G(258), u3a["1"][1])); b.wire((G(258), u3a["1"][1]), u3a["1"]); b.junction(u3a["1"])

    # R9 (100R) + Symmetric 4x Antiparallel 1N4148W Clamp (D11..D18) -> DAISY_AUDIO_IN
    r9 = b.place("Device:R", "R9", "100", G(264), G(54), ang=90, footprint=R0603, lcsc="C22775", mpn="0603WAF1000T5E", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    b.wire(u3a["1"], r9["2"])
    x_cl_pos, x_cl_neg, x_out_d = G(278), G(288), G(298)
    b.wire(r9["1"], (x_out_d, G(54)))
    b.junction((x_cl_pos, G(54))); b.junction((x_cl_neg, G(54)))
    b.glabel("DAISY_AUDIO_IN", (x_out_d, G(54)), ang=0, shape="output")

    # Positive clamp string D11..D14 (ang=90: Pin 2 A top, Pin 1 K bottom)
    prev = (x_cl_pos, G(54))
    for idx_d, ref_d in enumerate(["D11", "D12", "D13", "D14"]):
        yc = G(60 + idx_d * 8)
        dp = b.place("Device:D", ref_d, "1N4148W", x_cl_pos, yc, ang=90, footprint="Diode_SMD:D_SOD-123", lcsc="C81598", mpn="1N4148W", vrating="100V", props=SP_D1N4148, ref_off=(-4.5, 0), val_off=(4.5, 0))
        b.wire(prev, dp["2"])
        prev = dp["1"]
    b.wire(prev, b.pwr("GND", x_cl_pos, G(92), ang=0))

    # Negative clamp string D15..D18 (ang=270: Pin 1 K top, Pin 2 A bottom)
    prev = (x_cl_neg, G(54))
    for idx_d, ref_d in enumerate(["D15", "D16", "D17", "D18"]):
        yc = G(60 + idx_d * 8)
        dn = b.place("Device:D", ref_d, "1N4148W", x_cl_neg, yc, ang=270, footprint="Diode_SMD:D_SOD-123", lcsc="C81598", mpn="1N4148W", vrating="100V", props=SP_D1N4148, ref_off=(-4.5, 0), val_off=(4.5, 0))
        b.wire(prev, dn["1"])
        prev = dn["2"]
    b.wire(prev, b.pwr("GND", x_cl_neg, G(92), ang=0))

    # =========================================================================
    # ZONE 3: DAISY SEED, SATELLITE / ENCODER HEADERS & DECOUPLING (Bottom-Left)
    # =========================================================================
    b.box(14, 134, 184, 282)
    b.text("3. DAISY SEED (3V3_A ISOLATED, D15=PIN22), HEADERS & OP-AMP DECOUPLING", 16.5, 139)

    j_dl = b.place(
        "Connector_Generic:Conn_01x20", "J_DAISY_L1", "B-2200S20P-A120", G(34), G(148),
        footprint="Connector_PinSocket_2.54mm:PinSocket_1x20_P2.54mm_Vertical",
        lcsc="C124410", mpn="B-2200S20P-A120", exclude_from_sim="yes",
        notes="Daisy Seed Left Header Pins 1..20", ref_off=(-8, -28), val_off=(6, -28),
    )
    dl_map = {
        "12": ("I2C1_SCL", "bidirectional"),
        "13": ("I2C1_SDA", "bidirectional"),
        "16": ("DAISY_AUDIO_IN", "input"),
        "17": ("GND", None),
        "18": ("DAISY_AUDIO_OUT", "output"),
        "20": ("GND", None),
    }
    for i in range(1, 21):
        p = j_dl[str(i)]
        if str(i) in dl_map:
            nn, sh = dl_map[str(i)]
            st = (p[0] - G(6), p[1])
            b.wire(p, st)
            if nn == "GND":
                b.wire(st, b.pwr("GND", st[0] - G(2), st[1], ang=0))
            else:
                b.glabel(nn, st, ang=180, shape=sh)
        else:
            b.nc(p)

    j_dr = b.place(
        "Connector_Generic:Conn_01x20", "J_DAISY_R1", "B-2200S20P-A120", G(76), G(148),
        footprint="Connector_PinSocket_2.54mm:PinSocket_1x20_P2.54mm_Vertical",
        lcsc="C124410", mpn="B-2200S20P-A120", exclude_from_sim="yes",
        notes="Daisy Seed Right Header Pins 21..40 (Pin 1=Daisy 21 .. Pin 20=Daisy 40)",
        ref_off=(-8, -28), val_off=(6, -28),
    )
    dr_map = {
        "1": ("3V3_A", None),
        "2": ("GPIO_ENC_A_D15", "bidirectional"),
        "3": ("GPIO_ENC_B_D16", "bidirectional"),
        "4": ("GPIO_ENC_SW_D17", "bidirectional"),
        "18": ("3V3_D", None),
        "19": ("+5V", None),
        "20": ("GND", None),
    }
    for i in range(1, 21):
        p = j_dr[str(i)]
        if str(i) in dr_map:
            nn, sh = dr_map[str(i)]
            st = (p[0] - G(6), p[1])
            b.wire(p, st)
            if nn in ("GND", "+5V"):
                b.wire(st, b.pwr(nn, st[0] - G(2), st[1], ang=0))
            elif nn in ("3V3_D", "3V3_A"):
                b.wire(st, b.pwr(nn, st[0] - G(2), st[1], ang=180, pwr_flag=True))
            else:
                b.glabel(nn, st, ang=180, shape=sh)
        else:
            b.nc(p)

    # U6 2x10 Right-Angle Faceplate Header
    u6 = b.place(
        "Connector_Generic:Conn_02x10_Odd_Even", "U6", "2541WR-2x10P", G(116), G(136),
        footprint="Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Horizontal",
        lcsc="C5383093", mpn="2541WR-2x10P", exclude_from_sim="yes",
        ref_off=(-6, -15), val_off=(8, -15),
    )
    for i in range(1, 21):
        p = u6[str(i)]
        dx = -G(6) if (i % 2 == 1) else G(6)
        st = (p[0] + dx, p[1])
        b.wire(p, st)
        if i == 15:
            b.glabel("I2C1_SCL", st, ang=180, shape="output")
        elif i == 17:
            b.glabel("I2C1_SDA", st, ang=180, shape="bidirectional")
        elif i == 20:
            b.wire(st, b.pwr("3V3_D", st[0] + G(2), st[1], ang=0))
        else:
            b.wire(st, b.pwr("GND", st[0] + (G(2) if dx > 0 else -G(2)), st[1], ang=0))

    # J_ENC1 1x5 Right-Angle Encoder Header
    jenc = b.place(
        "Connector_Generic:Conn_01x05", "J_ENC1", "HX_PZ2.54-1x5P_WZ", G(118), G(168),
        footprint="Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal",
        lcsc="C32713264", mpn="HX PZ2.54-1x5P WZ", exclude_from_sim="yes",
        ref_off=(-6, -9), val_off=(6, -9),
    )
    enc_map = {"1": "GPIO_ENC_SW_D17", "2": "GND", "3": "GPIO_ENC_B_D16", "4": "GND", "5": "GPIO_ENC_A_D15"}
    for i in range(1, 6):
        p = jenc[str(i)]
        st = (p[0] - G(6), p[1])
        b.wire(p, st)
        nn = enc_map[str(i)]
        if nn == "GND":
            b.wire(st, b.pwr("GND", st[0] - G(2), st[1], ang=0))
        else:
            b.glabel(nn, st, ang=180, shape="input")

    # Op-Amp Power Units U2C, U3C, U4C, U7C + Spare U4B unity follower
    sock_notes = "Machined DIP-8 socket C2874007 (IC254V-12-08-0743): install OPA1656IDR on SOIC8-to-DIP8 adapter or dual DIP-8 op-amp"
    for idx_u, ref_u in enumerate(["U2", "U3", "U4", "U7"]):
        ux = G(30 + idx_u * 20)
        uy = G(190)
        fp_u = DIP8_SOCK if ref_u in ("U2", "U7") else SOIC8
        lcsc_u = "C2874007" if ref_u in ("U2", "U7") else "C1849431"
        mpn_u = "OPA1656_ON_DIP8_SOCKET" if ref_u in ("U2", "U7") else "OPA1656IDR"
        notes_u = sock_notes if ref_u in ("U2", "U7") else ""
        pu = b.place("Amplifier_Operational:LM2904", ref_u, "OPA1656", ux, uy, ang=0, unit=3, footprint=fp_u, lcsc=lcsc_u, mpn=mpn_u, vrating="36V", notes=notes_u, props=SP_OPA, ref_off=(3, -2), val_off=(3, 2))
        b.wire(pu["8"], b.pwr("+16V", pu["8"][0], pu["8"][1] - G(2), ang=0))
        b.wire(pu["4"], b.pwr("-16V", pu["4"][0], pu["4"][1] + G(2), ang=270))

    u4b = b.place("Amplifier_Operational:LM2904", "U4", "OPA1656", G(122), G(190), ang=0, unit=2, footprint=SOIC8, lcsc="C1849431", mpn="OPA1656IDR", vrating="36V", props=SP_OPA, ref_off=(-2, -7), val_off=(4, 7))
    b.wire(b.pwr("GND", u4b["5"][0] - G(3), u4b["5"][1], ang=0), u4b["5"])
    b.wire(u4b["6"], (G(114), u4b["6"][1])); b.wire((G(114), u4b["6"][1]), (G(114), G(198))); b.wire((G(114), G(198)), (G(130), G(198))); b.wire((G(130), G(198)), u4b["7"])

    # Decoupling caps (100nF 50V X7R)
    b.text("POWER & OP-AMP LOCAL DECOUPLING (100nF 50V X7R)", 16.5, 250, size=1.35)
    dec_specs = [
        ("C6", "+5V", "GND", 20, 210),
        ("C7", "3V3_D", "GND", 32, 210),
        ("C8", "3V3_A", "GND", 44, 210),
        ("C17", "+16V", "GND", 56, 210),
        ("C18", "GND", "-16V", 68, 210),
        ("C19", "+16V", "GND", 80, 210),
        ("C20", "GND", "-16V", 92, 210),
        ("C21", "+16V", "GND", 104, 210),
        ("C22", "GND", "-16V", 116, 210),
        ("C24", "+16V", "GND", 128, 210),
        ("C25", "GND", "-16V", 140, 210),
    ]
    for cref, top_n, bot_n, gx, gy in dec_specs:
        cx, cy = G(gx), G(gy)
        cp = b.place("Device:C", cref, "100nF", cx, cy, ang=0, footprint=C0603, lcsc="C14663", mpn="CC0603KRX7R9BB104", vrating="50V", props=SP_C, ref_off=(-4, -1), val_off=(-4, 1.8))
        b.wire(b.pwr(top_n, cx, cy - G(5), ang=0), cp["1"])
        b.wire(cp["2"], b.pwr(bot_n, cx, cy + G(5), ang=270 if bot_n == "-16V" else 0))

    # =========================================================================
    # ZONE 4: MAKE-UP GAIN, 10k LOW-NOISE CCOS, BAV21W +48V CLAMP & SOCKETED U7
    # =========================================================================
    b.box(188, 134, 406, 256)
    b.text("4. LINEAR MAKE-UP GAIN (+10.55dB), 10k LOW-NOISE CCOS, BAV21W +48V CLAMP & SOCKETED U7", 190.5, 139)

    b.glabel("DAISY_AUDIO_OUT", (G(160), G(130)), ang=180, shape="input")
    r30 = b.place("Device:R", "R30", "47k", G(164), G(140), ang=0, footprint=R0603, lcsc="C326725", mpn="RT0603BRD0747KL", vrating="75V", props=SP_R, ref_off=(-4.5, 0), val_off=(4.5, 0))
    b.wire((G(160), G(130)), (G(170), G(130))); b.junction((G(164), G(130))); b.wire((G(164), G(130)), r30["1"]); b.wire(r30["2"], b.pwr("GND", G(164), G(146), ang=0))
    r10 = b.place("Device:R", "R10", "1k", G(174), G(130), ang=90, footprint=R0603, lcsc="C110776", mpn="RT0603BRD071KL", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    b.wire((G(170), G(130)), r10["2"])
    u3b = b.place("Amplifier_Operational:LM2904", "U3", "OPA1656", G(188), G(132), ang=0, unit=2, footprint=SOIC8, lcsc="C1849431", mpn="OPA1656IDR", vrating="36V", props=SP_OPA, ref_off=(-2, -7), val_off=(4, 7))
    b.wire(r10["1"], u3b["5"])

    b.wire(u3b["6"], (G(180), u3b["6"][1])); b.junction((G(180), u3b["6"][1]))
    r12 = b.place("Device:R", "R12", "4.22k", G(176), G(142), ang=0, footprint=R0603, lcsc="C860418", mpn="RT0603BRB074K22L", vrating="75V", props=SP_R, ref_off=(-4.5, 0), val_off=(4.5, 0))
    b.wire((G(180), u3b["6"][1]), (G(176), u3b["6"][1])); b.wire((G(176), u3b["6"][1]), r12["1"]); b.wire(r12["2"], b.pwr("GND", G(176), G(148), ang=0))

    r11 = b.place("Device:R", "R11", "10k", G(188), G(144), ang=90, footprint=R0603, lcsc="C95204", mpn="RT0603BRD0710KL", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    c26 = b.place("Device:C", "C26", "47pF", G(188), G(151), ang=90, footprint=C0603, lcsc="C1671", mpn="CL10C470JB8NNNC", vrating="50V", props=SP_C, ref_off=(0, -3), val_off=(0, 3))
    b.wire((G(180), u3b["6"][1]), (G(180), G(151))); b.junction((G(180), G(144))); b.wire((G(180), G(144)), r11["2"]); b.wire((G(180), G(151)), c26["2"])
    b.wire(r11["1"], (G(196), G(144))); b.wire(c26["1"], (G(196), G(151))); b.wire((G(196), G(151)), (G(196), G(144))); b.junction((G(196), G(144)))
    b.wire((G(196), G(144)), (G(196), u3b["7"][1])); b.wire((G(196), u3b["7"][1]), u3b["7"]); b.junction(u3b["7"])

    vdrv_p_x = G(204)
    b.wire(u3b["7"], (vdrv_p_x, u3b["7"][1])); b.junction((vdrv_p_x, u3b["7"][1]))

    # U4A Unity Inverter -> V_DRV_N (10k low-noise + 47pF)
    r13 = b.place("Device:R", "R13", "10k", G(212), G(170), ang=90, footprint=R0603, lcsc="C95204", mpn="RT0603BRD0710KL", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    b.wire((vdrv_p_x, u3b["7"][1]), (vdrv_p_x, G(170))); b.wire((vdrv_p_x, G(170)), r13["2"])
    u4a = b.place("Amplifier_Operational:LM2904", "U4", "OPA1656", G(226), G(168), ang=0, unit=1, footprint=SOIC8, lcsc="C1849431", mpn="OPA1656IDR", vrating="36V", props=SP_OPA, ref_off=(-2, -7), val_off=(4, 7))
    b.wire(r13["1"], u4a["2"]); b.junction(u4a["2"])
    b.wire(b.pwr("GND", u4a["3"][0] - G(3), u4a["3"][1], ang=0), u4a["3"])
    r14 = b.place("Device:R", "R14", "10k", G(226), G(180), ang=90, footprint=R0603, lcsc="C95204", mpn="RT0603BRD0710KL", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    c27 = b.place("Device:C", "C27", "47pF", G(226), G(187), ang=90, footprint=C0603, lcsc="C1671", mpn="CL10C470JB8NNNC", vrating="50V", props=SP_C, ref_off=(0, -3), val_off=(0, 3))
    b.wire(u4a["2"], (G(218), u4a["2"][1])); b.wire((G(218), u4a["2"][1]), (G(218), G(187))); b.junction((G(218), G(180))); b.wire((G(218), G(180)), r14["2"]); b.wire((G(218), G(187)), c27["2"])
    b.wire(r14["1"], (G(234), G(180))); b.wire(c27["1"], (G(234), G(187))); b.wire((G(234), G(187)), (G(234), G(180))); b.junction((G(234), G(180)))
    b.wire((G(234), G(180)), (G(234), u4a["1"][1])); b.wire((G(234), u4a["1"][1]), u4a["1"]); b.junction(u4a["1"])

    vdrv_p = (G(242), u3b["7"][1])
    vdrv_n = (G(240), u4a["1"][1])
    b.wire((vdrv_p_x, u3b["7"][1]), vdrv_p)
    b.wire(u4a["1"], vdrv_n)

    # U7A (+OUT_P CCOS half, DIP-8 socketed + 10k low-noise)
    u7_notes = "Machined DIP-8 socket C2874007 (IC254V-12-08-0743): install OPA1656IDR on SOIC8-to-DIP8 adapter or dual DIP-8 op-amp"
    u7a = b.place("Amplifier_Operational:LM2904", "U7", "OPA1656", G(272), G(134), ang=0, unit=1, footprint=DIP8_SOCK, lcsc="C2874007", mpn="OPA1656_ON_DIP8_SOCKET", vrating="36V", notes=u7_notes, props=SP_OPA, ref_off=(-2, -7), val_off=(4, 7))
    r15 = b.place("Device:R", "R15", "10k", G(256), u7a["2"][1], ang=90, footprint=R0603, lcsc="C95204", mpn="RT0603BRD0710KL", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    r17 = b.place("Device:R", "R17", "10k", G(256), u7a["3"][1], ang=90, footprint=R0603, lcsc="C95204", mpn="RT0603BRD0710KL", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    r18 = b.place("Device:R", "R18", "10k", G(256), u7a["3"][1] - G(7), ang=90, footprint=R0603, lcsc="C95204", mpn="RT0603BRD0710KL", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    b.ortho_wire(vdrv_n, r15["2"], mid_x=G(240))
    b.ortho_wire(vdrv_p, r17["2"], mid_x=G(244))
    b.wire(r15["1"], u7a["2"]); b.junction(u7a["2"])
    b.wire(r17["1"], u7a["3"]); b.junction(u7a["3"])
    b.wire(r18["1"], (G(264), r18["1"][1])); b.wire((G(264), r18["1"][1]), u7a["3"])

    r16 = b.place("Device:R", "R16", "10k", G(272), G(146), ang=90, footprint=R0603, lcsc="C95204", mpn="RT0603BRD0710KL", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    c28 = b.place("Device:C", "C28", "47pF", G(272), G(153), ang=90, footprint=C0603, lcsc="C1671", mpn="CL10C470JB8NNNC", vrating="50V", props=SP_C, ref_off=(0, -3), val_off=(0, 3))
    b.wire(u7a["2"], (G(264), u7a["2"][1])); b.wire((G(264), u7a["2"][1]), (G(264), G(153))); b.junction((G(264), G(146))); b.wire((G(264), G(146)), r16["2"]); b.wire((G(264), G(153)), c28["2"])
    b.wire(r16["1"], (G(280), G(146))); b.wire(c28["1"], (G(280), G(153))); b.wire((G(280), G(153)), (G(280), G(146))); b.junction((G(280), G(146)))
    b.wire((G(280), G(146)), (G(280), u7a["1"][1])); b.wire((G(280), u7a["1"][1]), u7a["1"]); b.junction(u7a["1"])

    r19 = b.place("Device:R", "R19", "49.9", G(288), u7a["1"][1], ang=90, footprint=R1206, lcsc="C728678", mpn="RT1206BRE0749R9L", vrating="200V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    b.wire(u7a["1"], r19["2"])
    b.wire(r19["1"], (G(312), u7a["1"][1])); b.junction((G(296), u7a["1"][1])); b.junction((G(302), u7a["1"][1])); b.junction((G(308), u7a["1"][1]))
    b.glabel("OUT_P", (G(312), u7a["1"][1]), ang=0, shape="output")
    r20 = b.place("Device:R", "R20", "10k", G(296), u7a["1"][1] + G(8), ang=0, footprint=R0603, lcsc="C95204", mpn="RT0603BRD0710KL", vrating="75V", props=SP_R, ref_off=(-4.5, 0), val_off=(4.5, 0))
    b.wire((G(296), u7a["1"][1]), r20["1"]); b.wire(r20["2"], b.pwr("GND", G(296), u7a["1"][1] + G(14), ang=0))
    c39 = b.place("Device:C", "C39", "220pF", G(302), u7a["1"][1] + G(8), ang=0, footprint=C0805, lcsc="C113819", mpn="CC0805JRNPO0BN221", vrating="100V", props=SP_C, ref_off=(-4.5, 0), val_off=(4.5, 0))
    wire_vert(c39, G(302), u7a["1"][1], u7a["1"][1] + G(14))
    b.pwr("GND", G(302), u7a["1"][1] + G(14), ang=0)

    # U7B (-OUT_N CCOS half, DIP-8 socketed + 10k low-noise)
    u7b = b.place("Amplifier_Operational:LM2904", "U7", "OPA1656", G(272), G(176), ang=0, unit=2, footprint=DIP8_SOCK, lcsc="C2874007", mpn="OPA1656_ON_DIP8_SOCKET", vrating="36V", notes=u7_notes, props=SP_OPA, ref_off=(-2, -7), val_off=(4, 7))
    r21 = b.place("Device:R", "R21", "10k", G(256), u7b["6"][1], ang=90, footprint=R0603, lcsc="C95204", mpn="RT0603BRD0710KL", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    r23 = b.place("Device:R", "R23", "10k", G(256), u7b["5"][1], ang=90, footprint=R0603, lcsc="C95204", mpn="RT0603BRD0710KL", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    r24 = b.place("Device:R", "R24", "10k", G(256), u7b["5"][1] - G(7), ang=90, footprint=R0603, lcsc="C95204", mpn="RT0603BRD0710KL", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    b.ortho_wire(vdrv_p, r21["2"], mid_x=G(244)); b.junction((G(244), r17["2"][1]))
    b.ortho_wire(vdrv_n, r23["2"], mid_x=G(240)); b.junction((G(240), r15["2"][1]))
    b.wire(r21["1"], u7b["6"]); b.junction(u7b["6"])
    b.wire(r23["1"], u7b["5"]); b.junction(u7b["5"])
    b.wire(r24["1"], (G(264), r24["1"][1])); b.wire((G(264), r24["1"][1]), u7b["5"])

    r22 = b.place("Device:R", "R22", "10k", G(272), G(188), ang=90, footprint=R0603, lcsc="C95204", mpn="RT0603BRD0710KL", vrating="75V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    c29 = b.place("Device:C", "C29", "47pF", G(272), G(195), ang=90, footprint=C0603, lcsc="C1671", mpn="CL10C470JB8NNNC", vrating="50V", props=SP_C, ref_off=(0, -3), val_off=(0, 3))
    b.wire(u7b["6"], (G(264), u7b["6"][1])); b.wire((G(264), u7b["6"][1]), (G(264), G(195))); b.junction((G(264), G(188))); b.wire((G(264), G(188)), r22["2"]); b.wire((G(264), G(195)), c29["2"])
    b.wire(r22["1"], (G(280), G(188))); b.wire(c29["1"], (G(280), G(195))); b.wire((G(280), G(195)), (G(280), G(188))); b.junction((G(280), G(188)))
    b.wire((G(280), G(188)), (G(280), u7b["7"][1])); b.wire((G(280), u7b["7"][1]), u7b["7"]); b.junction(u7b["7"])

    r25 = b.place("Device:R", "R25", "49.9", G(288), u7b["7"][1], ang=90, footprint=R1206, lcsc="C728678", mpn="RT1206BRE0749R9L", vrating="200V", props=SP_R, ref_off=(0, -3), val_off=(0, 3))
    b.wire(u7b["7"], r25["2"])
    b.wire(r25["1"], (G(312), u7b["7"][1])); b.junction((G(296), u7b["7"][1])); b.junction((G(302), u7b["7"][1])); b.junction((G(308), u7b["7"][1]))
    b.glabel("OUT_N", (G(312), u7b["7"][1]), ang=0, shape="output")
    r26 = b.place("Device:R", "R26", "10k", G(296), u7b["7"][1] + G(8), ang=0, footprint=R0603, lcsc="C95204", mpn="RT0603BRD0710KL", vrating="75V", props=SP_R, ref_off=(-4.5, 0), val_off=(4.5, 0))
    b.wire((G(296), u7b["7"][1]), r26["1"]); b.wire(r26["2"], b.pwr("GND", G(296), u7b["7"][1] + G(14), ang=0))
    c40 = b.place("Device:C", "C40", "220pF", G(302), u7b["7"][1] + G(8), ang=0, footprint=C0805, lcsc="C113819", mpn="CC0805JRNPO0BN221", vrating="100V", props=SP_C, ref_off=(-4.5, 0), val_off=(4.5, 0))
    wire_vert(c40, G(302), u7b["7"][1], u7b["7"][1] + G(14))
    b.pwr("GND", G(302), u7b["7"][1] + G(14), ang=0)

    # Cross-sense taps directly using OUT_P / OUT_N (zero multiple_net_names warning)
    b.glabel("OUT_N", r18["2"], ang=180, shape="input")
    b.glabel("OUT_P", r24["2"], ang=180, shape="input")

    # Output rail clamps D7..D10 (BAV21W 250V)
    d7 = b.place("Device:D", "D7", "BAV21W", G(308), u7a["1"][1] - G(5), ang=270, footprint="Diode_SMD:D_SOD-123", lcsc="C113947", mpn="BAV21W", vrating="250V", props=SP_DBAV21W, ref_off=(-4.5, 0), val_off=(4.5, 0))
    d8 = b.place("Device:D", "D8", "BAV21W", G(308), u7a["1"][1] + G(5), ang=270, footprint="Diode_SMD:D_SOD-123", lcsc="C113947", mpn="BAV21W", vrating="250V", props=SP_DBAV21W, ref_off=(-4.5, 0), val_off=(4.5, 0))
    b.wire(b.pwr("+16V", G(308), u7a["1"][1] - G(10), ang=0), d7["1"])
    b.wire(d7["2"], (G(308), u7a["1"][1])); b.wire((G(308), u7a["1"][1]), d8["1"])
    b.wire(d8["2"], b.pwr("-16V", G(308), u7a["1"][1] + G(10), ang=270))

    d9 = b.place("Device:D", "D9", "BAV21W", G(308), u7b["7"][1] - G(5), ang=270, footprint="Diode_SMD:D_SOD-123", lcsc="C113947", mpn="BAV21W", vrating="250V", props=SP_DBAV21W, ref_off=(-4.5, 0), val_off=(4.5, 0))
    d10 = b.place("Device:D", "D10", "BAV21W", G(308), u7b["7"][1] + G(5), ang=270, footprint="Diode_SMD:D_SOD-123", lcsc="C113947", mpn="BAV21W", vrating="250V", props=SP_DBAV21W, ref_off=(-4.5, 0), val_off=(4.5, 0))
    b.wire(b.pwr("+16V", G(308), u7b["7"][1] - G(10), ang=0), d9["1"])
    b.wire(d9["2"], (G(308), u7b["7"][1])); b.wire((G(308), u7b["7"][1]), d10["1"])
    b.wire(d10["2"], b.pwr("-16V", G(308), u7b["7"][1] + G(10), ang=270))

    sch_text = (
        f'(kicad_sch\n'
        f'  (version 20250114)\n'
        f'  (generator "build_october_surprise_sch")\n'
        f'  (generator_version "1.0")\n'
        f'  (uuid "{ROOT_UUID}")\n'
        f'  (paper "A3")\n'
        f'  (title_block\n'
        f'    (title "ICIO500 October Surprise (Carrier Rev 2)")\n'
        f'    (date "2026-11-25")\n'
        f'    (rev "2.0")\n'
        f'    (company "ICIO")\n'
        f'    (comment 1 "Discrete OPA1656 3-Op-Amp INA + DRV135-Topology CCOS (Zero EOL ICs)")\n'
        f'    (comment 2 "0 dB Unity Pass-Through | +20 dBu Headroom | 4x 1N4148W Bipolar Clamp")\n'
        f'  )\n'
        f'  (lib_symbols\n'
        + "\n".join("    " + s for s in b.lib_symbols)
        + "\n  )\n"
        + "\n".join(b.elements)
        + f'\n  (sheet_instances\n    (path "/" (page "1"))\n  )\n'
        + ')\n'
    )
    os.makedirs(os.path.dirname(OUT_SCH), exist_ok=True)
    open(OUT_SCH, "w", encoding="utf-8").write(sch_text)
    print(f"Wrote {OUT_SCH} ({len(sch_text)} bytes)")


if __name__ == "__main__":
    build()
