"""
Build the ICIO500 2-Layer Active Satellite PCB (kicad/faceplate_satellite.kicad_pcb).

Designed to sit completely hidden behind a swappable front faceplate (3.18 mm Baltic Birch
with smoked acrylic VU inlay, or 3.00 mm full smoked acrylic):
  - Footprint outline: 35.10 x 113.35 mm (X in [1.50, 36.60], Y in [10.00, 123.35] in native VPR coords)
  - Standard 2-layer 0.8 mm FR4 (zero blind slots!), matte black soldermask, zero F.Cu components
  - Two NPTH Ø2.70 mm M2.5 mounting holes near the top (5.05, 24.00) and (33.05, 24.00)
  - 100% compatible with in-production Carrier (BR1/BR2, U6->J1) and Encoder (PEC11R M7) PCBs
  - D1..D16 reverse-mount gull-wing LEDs (XL-3216...-FB) on B.Cu shining through regular full
    1.92 x 1.68 mm NPTH oval slots cleanly across F.Cu
"""

import math
import os
import pcbnew


def mm(val):
    return int(round(val * 1e6))


def run():
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(2)
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(mm(0.8))
    ds.m_CopperEdgeClearance = mm(0.25)
    ds.m_HoleClearance = mm(0.20)
    ds.m_TrackClearance = mm(0.20)
    ds.m_SolderMaskExpansion = mm(0.05)

    # 1. Edge.Cuts: Inset satellite PCB [1.50..36.60] x [10.00..123.35] (35.10 x 113.35 mm)
    X_MIN, X_MAX = 1.50, 36.60
    Y_MIN, Y_MAX = 10.00, 123.35
    outline_pts = [(X_MIN, Y_MIN), (X_MAX, Y_MIN), (X_MAX, Y_MAX), (X_MIN, Y_MAX)]
    for i in range(4):
        p1 = outline_pts[i]
        p2 = outline_pts[(i + 1) % 4]
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pcbnew.VECTOR2I(mm(p1[0]), mm(p1[1])))
        seg.SetEnd(pcbnew.VECTOR2I(mm(p2[0]), mm(p2[1])))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(mm(0.10))
        board.Add(seg)

    # Encoder M7 bushing cutout (Ø7.20 mm) & anti-rotation clearance circle (Ø2.20 mm)
    for cx, cy, r_mm in [(19.050, 109.350, 3.600), (11.550, 109.350, 1.100)]:
        circ = pcbnew.PCB_SHAPE(board)
        circ.SetShape(pcbnew.SHAPE_T_CIRCLE)
        circ.SetFilled(False)
        circ.SetCenter(pcbnew.VECTOR2I(mm(cx), mm(cy)))
        circ.SetRadius(mm(r_mm))
        circ.SetLayer(pcbnew.Edge_Cuts)
        circ.SetWidth(mm(0.10))
        board.Add(circ)

    # 2. Nets
    def get_or_create_net(name):
        net = board.FindNet(name)
        if not net:
            net = pcbnew.NETINFO_ITEM(board, name)
            board.Add(net)
        return net

    gnd = get_or_create_net("GND")
    pwr = get_or_create_net("+3V3")
    pwr_in = get_or_create_net("+3V3_IN")
    sda = get_or_create_net("SDA")
    scl = get_or_create_net("SCL")

    led_nets = [get_or_create_net(f"LED_{i+1}") for i in range(10)]
    led_mid_nets = [get_or_create_net(f"Net-(D{i+1}-Pad2)") for i in range(10)]

    rgb_nets = {
        "R": get_or_create_net("RGB_R"),
        "G": get_or_create_net("RGB_G"),
        "B": get_or_create_net("RGB_B"),
    }
    rgb_mid_nets = [get_or_create_net(f"Net-(D{11+i}-Pad1)") for i in range(6)]

    # 3. Footprints (100% SMT on B.Cu; top M2.5 mounting holes are NPTH)
    lib_base = r"C:\Program Files\KiCad\10.0\share\kicad\footprints"

    def load_fp(pretty_lib, fp_name, ref):
        fp = pcbnew.FootprintLoad(os.path.join(lib_base, pretty_lib), fp_name)
        fp.SetReference(ref)
        return fp

    def strip_fp_silks(fp):
        for g in fp.GraphicalItems():
            if g.GetLayerName() in ("F.Silkscreen", "B.Silkscreen", "F.SilkS", "B.SilkS"):
                g.SetLayer(pcbnew.Dwgs_User)
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)

    # M2.5 Top Screw Mounting Holes (NPTH Ø2.70 mm, R=2.85 mm copper keepout for M2.5 nut)
    m25_holes = [("MH_TOP_L", 5.050, 24.000), ("MH_TOP_R", 33.050, 24.000)]
    for ref, mx, my in m25_holes:
        mh = load_fp("MountingHole.pretty", "MountingHole_2.7mm_M2.5", ref)
        mh.SetPosition(pcbnew.VECTOR2I(mm(mx), mm(my)))
        strip_fp_silks(mh)
        board.Add(mh)

    # J1 at (11.280, 75.000) on B.Cu -> mates 1:1 with Carrier U6
    j1 = load_fp("Connector_PinSocket_2.54mm.pretty", "PinSocket_2x10_P2.54mm_Vertical_SMD", "J1")
    j1.SetValue("Conn_02x10_Odd_Even")
    j1.SetPosition(pcbnew.VECTOR2I(mm(11.280), mm(75.000)))
    strip_fp_silks(j1)
    board.Add(j1)
    j1.Flip(j1.GetPosition(), False)

    j1_map = {"2": pwr_in, "3": sda, "5": scl}
    for pad in j1.Pads():
        pad.SetNet(j1_map.get(str(pad.GetNumber()), gnd))

    # BR1 & BR2 (Wuerth 7466303 M3 right-angle brackets on B.Cu -> mate with Carrier MH1/MH2)
    br_fps = {}
    for ref, by in [("BR1", 14.525), ("BR2", 118.825)]:
        br = load_fp("Mounting_Wuerth.pretty", "Mounting_Wuerth_WP-SMRA-M3_L7mm_7466303_Horizontal", ref)
        br.SetValue("WP-SMRA-M3")
        br.SetPosition(pcbnew.VECTOR2I(mm(10.310), mm(by)))
        strip_fp_silks(br)
        board.Add(br)
        br.Flip(br.GetPosition(), False)
        for p in br.Pads():
            p.SetNet(gnd)
            p.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
        br_fps[ref] = br

    def tune_rev_led_pads(fp):
        """Standard 1.92 x 1.68 mm NPTH oval slot + 0.80 x 1.60 mm pads at +/-1.625 mm (0.265 mm clearance)."""
        for p in fp.Pads():
            if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                p.SetSize(pcbnew.VECTOR2I(mm(1.92), mm(1.68)))
                p.SetDrillSize(pcbnew.VECTOR2I(mm(1.92), mm(1.68)))
            elif str(p.GetNumber()) == "1":
                p.SetPos(pcbnew.VECTOR2I(mm(-1.625), 0))
                p.SetSize(pcbnew.VECTOR2I(mm(0.80), mm(1.60)))
            elif str(p.GetNumber()) == "2":
                p.SetPos(pcbnew.VECTOR2I(mm(1.625), 0))
                p.SetSize(pcbnew.VECTOR2I(mm(0.80), mm(1.60)))

    # D1..D10 VU Bar Graph reverse-mount LEDs on B.Cu over full NPTH slots
    for i in range(10):
        wy = 20.000 + 8.000 * i
        d = load_fp("LED_SMD.pretty", "LED_1206_3216Metric_ReverseMount_Hole1.8x2.4mm", f"D{i+1}")
        tune_rev_led_pads(d)
        d.SetPosition(pcbnew.VECTOR2I(mm(19.050), mm(wy)))
        strip_fp_silks(d)
        board.Add(d)
        d.Flip(d.GetPosition(), False)
        for p in d.Pads():
            if str(p.GetNumber()) == "1":
                p.SetNet(led_mid_nets[i])
            elif str(p.GetNumber()) == "2":
                p.SetNet(pwr)

    # R1..R10 (0402) at (23.800, wy) on B.Cu -> leaves X=[24.65..28.00] open for vias/tracks
    for i in range(10):
        wy = 20.000 + 8.000 * i
        r = load_fp("Resistor_SMD.pretty", "R_0402_1005Metric", f"R{i+1}")
        if i == 0:
            r.SetValue("68R")
        elif i in (1, 2):
            r.SetValue("82R")
        else:
            r.SetValue("100R")
        r.SetPosition(pcbnew.VECTOR2I(mm(23.800), mm(wy)))
        r.SetOrientation(pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))
        strip_fp_silks(r)
        board.Add(r)
        r.Flip(r.GetPosition(), False)
        for p in r.Pads():
            if str(p.GetNumber()) == "1":
                p.SetNet(led_mid_nets[i])
            else:
                p.SetNet(led_nets[i])

    # D11..D16 Skirt RGBRGB ring around encoder (19.050, 109.350) + R16..R21 (100R)
    rgb_ring_specs = [
        (11, 16, "R", 19.050,  99.350, False),
        (12, 17, "G", 27.710, 104.350, False),
        (13, 18, "B", 27.710, 114.350, False),
        (14, 19, "R", 19.050, 119.350, False),
        (15, 20, "G", 10.390, 114.350, True),
        (16, 21, "B", 10.390, 104.350, True),
    ]
    for idx, (d_num, r_num, ch, dx, dy, rot180) in enumerate(rgb_ring_specs):
        d = load_fp("LED_SMD.pretty", "LED_1206_3216Metric_ReverseMount_Hole1.8x2.4mm", f"D{d_num}")
        tune_rev_led_pads(d)
        d.SetPosition(pcbnew.VECTOR2I(mm(dx), mm(dy)))
        if rot180:
            d.SetOrientation(pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))
        strip_fp_silks(d)
        board.Add(d)
        d.Flip(d.GetPosition(), False)
        for p in d.Pads():
            if str(p.GetNumber()) == "1":
                p.SetNet(rgb_mid_nets[idx])
            elif str(p.GetNumber()) == "2":
                p.SetNet(pwr)

        r = load_fp("Resistor_SMD.pretty", "R_0402_1005Metric", f"R{r_num}")
        r.SetValue("100R")
        rx = (dx - 3.400) if rot180 else (dx + 3.400)
        r.SetPosition(pcbnew.VECTOR2I(mm(rx), mm(dy)))
        if rot180:
            r.SetOrientation(pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))
        strip_fp_silks(r)
        board.Add(r)
        r.Flip(r.GetPosition(), False)
        for p in r.Pads():
            if str(p.GetNumber()) == "1":
                p.SetNet(rgb_nets[ch])
            else:
                p.SetNet(rgb_mid_nets[idx])

    # U1 (PCA9555PW) horizontal at (31.800, 52.000) matching exact 8614cab orientation (SetOrientation(90) + Flip)
    # South row Y=54.8625: Pin 12 (28.225) .. Pin 1 (35.375)
    # North row Y=49.1375: Pin 13 (28.225) .. Pin 24 (35.375)
    u1 = load_fp("Package_SO.pretty", "TSSOP-24_4.4x7.8mm_P0.65mm", "U1")
    u1.SetValue("PCA9555PW")
    u1.SetPosition(pcbnew.VECTOR2I(mm(31.800), mm(52.000)))
    u1.SetOrientation(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
    strip_fp_silks(u1)
    board.Add(u1)
    u1.Flip(u1.GetPosition(), False)

    u1_map = {
        "11": led_nets[0], "10": led_nets[1], "9": led_nets[2], "8": led_nets[3],
        "7":  led_nets[4], "6":  led_nets[5], "5": led_nets[6], "4": led_nets[7],
        "3":  gnd,         "2":  gnd,         "1": gnd,         "12": gnd,
        "13": led_nets[8], "14": led_nets[9],
        "15": rgb_nets["G"], "16": rgb_nets["B"], "17": rgb_nets["R"],
        "18": gnd,         "19": gnd,         "20": gnd,
        "21": gnd,         "22": scl,         "23": sda,        "24": pwr,
    }
    for pad in u1.Pads():
        num = str(pad.GetNumber())
        if num in u1_map:
            pad.SetNet(u1_map[num])
            if pad.GetNetname() == "GND":
                pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)

    # Power & I2C 0402 Passives cleanly North of U1 (Y=30.8..36.6, South of MH_TOP_R keepout Y=27.2)
    def add_passive_0402(lib, fp_name, ref, val, x, y, vert, net_a, net_b):
        """When horizontal (vert=False): net_a=West, net_b=East. When vertical (vert=True): net_a=North, net_b=South."""
        fp = load_fp(lib, fp_name, ref)
        fp.SetValue(val)
        fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        if vert:
            fp.SetOrientation(pcbnew.EDA_ANGLE(270, pcbnew.DEGREES_T))
        strip_fp_silks(fp)
        board.Add(fp)
        fp.Flip(fp.GetPosition(), False)
        for p in fp.Pads():
            coord = (p.GetPosition().y / 1e6 - y) if vert else (p.GetPosition().x / 1e6 - x)
            p.SetNet(net_a if coord < 0 else net_b)
        return fp

    fb1 = add_passive_0402("Inductor_SMD.pretty",  "L_0402_1005Metric", "FB1", "BLM15AX601SN1D", 34.865, 30.800, False, pwr_in, pwr)
    c1  = add_passive_0402("Capacitor_SMD.pretty", "C_0402_1005Metric", "C1",  "100nF",          34.865, 32.400, False, gnd,    pwr)
    c2  = add_passive_0402("Capacitor_SMD.pretty", "C_0402_1005Metric", "C2",  "10uF",           34.865, 34.000, False, gnd,    pwr)
    r12 = add_passive_0402("Resistor_SMD.pretty",  "R_0402_1005Metric", "R12", "4.7k",           34.075, 36.600, True,  pwr,    scl)
    r11 = add_passive_0402("Resistor_SMD.pretty",  "R_0402_1005Metric", "R11", "4.7k",           32.500, 36.600, True,  pwr,    sda)

    # 4. 2-Layer Routing Helpers (B.Cu + F.Cu with 0.30/0.60 mm vias)
    def track(x1, y1, x2, y2, net, layer=pcbnew.B_Cu, width=0.20):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
        t.SetWidth(mm(width))
        t.SetLayer(layer)
        t.SetNet(net)
        board.Add(t)

    def poly(pts, net, layer=pcbnew.B_Cu, width=0.20):
        for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
            track(x1, y1, x2, y2, net, layer=layer, width=width)

    def via(x, y, net, drill=0.30, size=0.60):
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        v.SetDrill(mm(drill))
        v.SetWidth(mm(size))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNet(net)
        board.Add(v)

    def pad_xy(fp, pred):
        for p in fp.Pads():
            if pred(p):
                return (p.GetPosition().x / 1e6, p.GetPosition().y / 1e6)
        raise RuntimeError(f"Pad not found on {fp.GetReference()}")

    u1_pins = {str(p.GetNumber()): (p.GetPosition().x / 1e6, p.GetPosition().y / 1e6) for p in u1.Pads()}

    # 4a. VU mid links D1..D10 Pad 1 (20.675) -> R1..R10 Pad 1 (23.290) on B.Cu
    for i in range(10):
        wy = 20.000 + 8.000 * i
        track(20.675, wy, 23.290, wy, led_mid_nets[i], pcbnew.B_Cu)

    # 4b. LED_1..LED_4: U1 South pins 11..8 -> B.Cu -> F.Cu West lanes -> R1..R4 Pad 2 (24.310)
    # Ordered so LED_4 stops lowest (44.00) on Westmost X=25.60, and LED_1 goes highest (20.00) on Eastmost X=27.40
    vu_lanes_top = [
        ("11", 0, 20.000, 27.400, 56.200),
        ("10", 1, 28.000, 26.800, 56.900),
        ("9",  2, 36.000, 26.200, 57.600),
        ("8",  3, 44.000, 25.600, 58.300),
    ]
    for pnum, lidx, ry, fx, vy in vu_lanes_top:
        px, py = u1_pins[pnum]
        poly([(px, py), (px, vy), (fx, vy)], led_nets[lidx], pcbnew.B_Cu)
        via(fx, vy, led_nets[lidx])
        poly([(fx, vy), (fx, ry), (25.250, ry)], led_nets[lidx], pcbnew.F_Cu)
        via(25.250, ry, led_nets[lidx])
        track(25.250, ry, 24.310, ry, led_nets[lidx], pcbnew.B_Cu)

    # 4c. LED_5 (Pin 7): via under F.Cu at Y=59.20 -> B.Cu at X=24.85 up to R5 (24.310, 52.000)
    p7x, p7y = u1_pins["7"]
    poly([(p7x, p7y), (p7x, 56.600)], led_nets[4], pcbnew.B_Cu)
    via(p7x, 56.600, led_nets[4])
    poly([(p7x, 56.600), (p7x, 59.200), (24.850, 59.200)], led_nets[4], pcbnew.F_Cu)
    via(24.850, 59.200, led_nets[4])
    poly([(24.850, 59.200), (24.850, 52.000), (24.310, 52.000)], led_nets[4], pcbnew.B_Cu)

    # 4d. LED_6..LED_8 (Pins 6..4) planar on B.Cu directly to R6..R8 Pad 2 (24.310, 60/68/76)
    for pnum, lidx, ry in [("6", 5, 60.000), ("5", 6, 68.000), ("4", 7, 76.000)]:
        px, py = u1_pins[pnum]
        poly([(px, py), (px, ry), (24.310, ry)], led_nets[lidx], pcbnew.B_Cu)

    # 4e. U1 North signal fanout (Pins 13..17): vertical B.Cu stubs -> vias -> F.Cu East bus (zero crossings)
    east_bus = [
        ("13", led_nets[8],   43.300, 35.200),
        ("14", led_nets[9],   44.300, 34.500),
        ("15", rgb_nets["G"], 45.300, 33.800),
        ("16", rgb_nets["B"], 46.300, 33.100),
        ("17", rgb_nets["R"], 47.300, 32.400),
    ]
    for pnum, net, vy, ex in east_bus:
        px, py = u1_pins[pnum]
        track(px, py, px, vy, net, pcbnew.B_Cu)
        via(px, vy, net)
        track(px, vy, ex, vy, net, pcbnew.F_Cu)

    # LED_9 -> R9 (24.310, 84.000) & LED_10 -> R10 (24.310, 92.000) via B.Cu taps under F.Cu lanes
    track(35.200, 43.300, 35.200, 84.000, led_nets[8], pcbnew.F_Cu)
    via(35.200, 84.000, led_nets[8])
    track(35.200, 84.000, 24.310, 84.000, led_nets[8], pcbnew.B_Cu)

    track(34.500, 44.300, 34.500, 92.000, led_nets[9], pcbnew.F_Cu)
    via(34.500, 92.000, led_nets[9])
    track(34.500, 92.000, 24.310, 92.000, led_nets[9], pcbnew.B_Cu)

    # RGB_G -> R17 (31.620, 104.350) & R20 (6.480, 114.350) via B.Cu cross-under to X=31.400
    track(33.800, 45.300, 33.800, 104.350, rgb_nets["G"], pcbnew.F_Cu)
    via(33.800, 104.350, rgb_nets["G"])
    track(33.800, 104.350, 31.620, 104.350, rgb_nets["G"], pcbnew.B_Cu)
    via(33.800, 95.000, rgb_nets["G"])
    track(33.800, 95.000, 31.400, 95.000, rgb_nets["G"], pcbnew.B_Cu)
    via(31.400, 95.000, rgb_nets["G"])
    poly([(31.400, 95.000), (4.900, 95.000), (4.900, 114.350)], rgb_nets["G"], pcbnew.F_Cu)
    via(4.900, 114.350, rgb_nets["G"])
    track(4.900, 114.350, 6.480, 114.350, rgb_nets["G"], pcbnew.B_Cu)

    # RGB_B -> R18 (31.620, 114.350) & R21 (6.480, 104.350) via B.Cu cross-under to X=31.400
    track(33.100, 46.300, 33.100, 114.350, rgb_nets["B"], pcbnew.F_Cu)
    via(33.100, 114.350, rgb_nets["B"])
    track(33.100, 114.350, 31.620, 114.350, rgb_nets["B"], pcbnew.B_Cu)
    via(33.100, 96.200, rgb_nets["B"])
    track(33.100, 96.200, 31.400, 96.200, rgb_nets["B"], pcbnew.B_Cu)
    via(31.400, 96.200, rgb_nets["B"])
    poly([(31.400, 96.200), (5.700, 96.200), (5.700, 103.200)], rgb_nets["B"], pcbnew.F_Cu)
    via(5.700, 103.200, rgb_nets["B"])
    poly([(5.700, 103.200), (5.700, 104.350), (6.480, 104.350)], rgb_nets["B"], pcbnew.B_Cu)

    # RGB_R -> R19 (22.960, 119.350) & R16 (22.960, 99.350) via X=24.50 F.Cu (clears encoder Ø7.20 hole <= 22.65)
    poly([(32.400, 47.300), (32.400, 119.350), (23.800, 119.350)], rgb_nets["R"], pcbnew.F_Cu)
    via(23.800, 119.350, rgb_nets["R"])
    track(23.800, 119.350, 22.960, 119.350, rgb_nets["R"], pcbnew.B_Cu)
    poly([(24.500, 119.350), (24.500, 99.350), (23.800, 99.350)], rgb_nets["R"], pcbnew.F_Cu)
    via(23.800, 99.350, rgb_nets["R"])
    track(23.800, 99.350, 22.960, 99.350, rgb_nets["R"], pcbnew.B_Cu)

    # 4f. D11..D16 Pad 1 -> R16..R21 Pad 2 on B.Cu
    for idx, (d_num, r_num, ch, dx, dy, rot180) in enumerate(rgb_ring_specs):
        if rot180:
            track(dx - 1.625, dy, dx - 2.890, dy, rgb_mid_nets[idx], pcbnew.B_Cu)
        else:
            track(dx + 1.625, dy, dx + 2.890, dy, rgb_mid_nets[idx], pcbnew.B_Cu)

    # 4g. +3V3 Anode Spine & Ring on B.Cu (vertical bar shifted to X=14.800 -> 0.525 mm clear of Ø7.20 encoder hole)
    track(17.425, 20.000, 17.425, 99.350, pwr, pcbnew.B_Cu, width=0.25)
    poly([(17.425, 99.350), (14.800, 99.350), (14.800, 119.350), (17.425, 119.350)], pwr, pcbnew.B_Cu, width=0.25)
    track(14.800, 104.350, 12.015, 104.350, pwr, pcbnew.B_Cu, width=0.25)  # D16 Pad 2
    track(14.800, 114.350, 12.015, 114.350, pwr, pcbnew.B_Cu, width=0.25)  # D15 Pad 2
    poly([(14.800, 104.900), (25.000, 104.900), (25.000, 104.350), (26.085, 104.350)], pwr, pcbnew.B_Cu, width=0.25)  # D12 Pad 2
    poly([(25.000, 104.900), (25.000, 114.350), (26.085, 114.350)], pwr, pcbnew.B_Cu, width=0.25)  # D13 Pad 2

    # 4h. +3V3, +3V3_IN, SDA, SCL Control & Power Bus (zero crossings on either layer!)
    p24x, p24y = u1_pins["24"]
    p23x, p23y = u1_pins["23"]
    p22x, p22y = u1_pins["22"]

    fb1_pw = pad_xy(fb1, lambda p: p.GetPosition().x / 1e6 < 34.865)
    fb1_pe = pad_xy(fb1, lambda p: p.GetPosition().x / 1e6 > 34.865)
    c1_pw  = pad_xy(c1,  lambda p: p.GetPosition().x / 1e6 < 34.865)
    c1_pe  = pad_xy(c1,  lambda p: p.GetPosition().x / 1e6 > 34.865)
    c2_pw  = pad_xy(c2,  lambda p: p.GetPosition().x / 1e6 < 34.865)
    c2_pe  = pad_xy(c2,  lambda p: p.GetPosition().x / 1e6 > 34.865)
    r12_pn = pad_xy(r12, lambda p: p.GetPosition().y / 1e6 < 36.600)
    r12_ps = pad_xy(r12, lambda p: p.GetPosition().y / 1e6 > 36.600)
    r11_pn = pad_xy(r11, lambda p: p.GetPosition().y / 1e6 < 36.600)
    r11_ps = pad_xy(r11, lambda p: p.GetPosition().y / 1e6 > 36.600)

    # +3V3 spine East at X=35.375 from U1 Pin 24 up to Y=29.00, around MH_TOP_R keepout to (17.425, 20.00)
    poly([(p24x, p24y), (35.375, 29.000), (29.800, 29.000), (29.800, 16.000), (17.425, 16.000), (17.425, 20.000)], pwr, pcbnew.B_Cu, width=0.25)
    track(c1_pe[0], c1_pe[1], 35.375, c1_pe[1], pwr, pcbnew.B_Cu, width=0.25)
    track(c2_pe[0], c2_pe[1], 35.375, c2_pe[1], pwr, pcbnew.B_Cu, width=0.25)
    track(fb1_pe[0], fb1_pe[1], 35.375, fb1_pe[1], pwr, pcbnew.B_Cu, width=0.25)
    # Horizontal +3V3 pullup header bar at Y=35.900 feeding R12 (34.075) & R11 (32.500)
    poly([(35.375, 35.900), (32.500, 35.900), r11_pn], pwr, pcbnew.B_Cu, width=0.25)
    track(34.075, 35.900, r12_pn[0], r12_pn[1], pwr, pcbnew.B_Cu, width=0.25)

    # +3V3_IN: FB1 Pad West (34.35, 30.80) -> B.Cu West to (18.60, 30.80) -> F.Cu hop over 17.425 at Y=32.00 ->
    # B.Cu at (15.95, 32.00) -> B.Cu straight down X=15.95 (sails under SDA/SCL on F.Cu!) -> J1 Pad 2 (13.80, 63.57)
    poly([fb1_pw, (31.000, 30.800), (31.000, 30.200), (29.500, 30.200), (29.500, 30.800), (18.600, 30.800)], pwr_in, pcbnew.B_Cu, width=0.25)
    via(18.600, 30.800, pwr_in)
    poly([(18.600, 30.800), (18.600, 32.000), (15.950, 32.000)], pwr_in, pcbnew.F_Cu, width=0.25)
    via(15.950, 32.000, pwr_in)
    poly([(15.950, 32.000), (15.950, 63.570), (13.800, 63.570)], pwr_in, pcbnew.B_Cu, width=0.25)

    # SCL: U1 Pin 22 (34.075) -> straight North on B.Cu through Y=39.60 into R12 South pad (34.075, 37.11),
    # and tee West at Y=39.60 -> via (18.60, 39.60) -> F.Cu outer rainbow X=10.50 -> (11.28, 68.65) -> J1 Pad 5
    track(p22x, p22y, 34.075, r12_ps[1], scl, pcbnew.B_Cu)
    track(34.075, 39.600, 18.600, 39.600, scl, pcbnew.B_Cu)
    via(18.600, 39.600, scl)
    poly([(18.600, 39.600), (10.500, 39.600), (10.500, 68.650), (11.280, 68.650)], scl, pcbnew.F_Cu)
    via(11.280, 68.650, scl)
    track(11.280, 68.650, 8.760, 68.650, scl, pcbnew.B_Cu)

    # SDA: U1 Pin 23 (34.725) -> via (34.725, 41.80) -> F.Cu bridge to (32.500, 41.80) -> F.Cu hop North to via (32.500, 38.20) -> B.Cu R11 South pad,
    # and West at Y=41.20 -> via (18.60, 41.20) -> F.Cu inner rainbow X=11.28 -> (11.28, 66.11) -> J1 Pad 3
    track(p23x, p23y, p23x, 41.800, sda, pcbnew.B_Cu)
    via(p23x, 41.800, sda)
    poly([(p23x, 41.800), (32.500, 41.800), (32.500, 38.200)], sda, pcbnew.F_Cu)
    via(32.500, 38.200, sda)
    track(32.500, 38.200, r11_ps[0], r11_ps[1], sda, pcbnew.B_Cu)
    via(32.500, 41.800, sda)
    track(32.500, 41.800, 18.600, 41.800, sda, pcbnew.B_Cu)
    via(18.600, 41.800, sda)
    poly([(18.600, 41.800), (11.280, 41.800), (11.280, 66.110)], sda, pcbnew.F_Cu)
    via(11.280, 66.110, sda)
    track(11.280, 66.110, 8.760, 66.110, sda, pcbnew.B_Cu)

    # 4i. Solid GND Ties & Stitching Vias (prevents any isolated copper islands or unplated pad splits)
    track(u1_pins["1"][0], u1_pins["1"][1], u1_pins["3"][0], u1_pins["3"][1], gnd, pcbnew.B_Cu)
    track(u1_pins["12"][0], u1_pins["12"][1], 27.200, u1_pins["12"][1], gnd, pcbnew.B_Cu)
    track(u1_pins["18"][0], u1_pins["18"][1], u1_pins["21"][0], u1_pins["21"][1], gnd, pcbnew.B_Cu)
    via(31.800, 52.000, gnd)
    track(u1_pins["18"][0], u1_pins["18"][1], 31.800, 52.000, gnd, pcbnew.B_Cu)

    # Tie C1 & C2 West GND pads into a stitching via cleanly East of SCL (34.075)
    poly([c1_pw, (33.500, 32.400), (33.500, 34.000), c2_pw], gnd, pcbnew.B_Cu)
    via(32.800, 33.200, gnd)
    track(33.500, 33.200, 32.800, 33.200, gnd, pcbnew.B_Cu)

    # Explicit BR1 & BR2 pad loops + GND stitching into continuous pours
    for ref, bx_tie, by_tie in [("BR1", 14.500, 12.500), ("BR2", 14.500, 121.000)]:
        pads = [(p.GetPosition().x / 1e6, p.GetPosition().y / 1e6) for p in br_fps[ref].Pads()]
        w_pads = sorted([p for p in pads if p[0] < 10.31], key=lambda p: p[1])
        e_pads = sorted([p for p in pads if p[0] > 10.31], key=lambda p: p[1])
        poly([w_pads[0], w_pads[1], e_pads[1], e_pads[0], w_pads[0]], gnd, pcbnew.B_Cu, width=0.30)
        track(e_pads[0][0], e_pads[0][1], bx_tie, by_tie, gnd, pcbnew.B_Cu, width=0.30)
        via(bx_tie, by_tie, gnd)

    # GND stitching vias linking F.Cu and B.Cu continuous GND pours
    for vx, vy in [
        (11.50, 28.00), (11.50, 36.00), (11.50, 88.00),
        (28.00, 88.00), (29.00, 121.00), (35.50, 121.00),
    ]:
        via(vx, vy, gnd)

    # 5. B.Silkscreen Pin 1 Dots & Board Label (kept clear of copper pads, NPTH holes & edges)
    def add_bsilk_dot(cx, cy, radius=0.30):
        dot = pcbnew.PCB_SHAPE(board)
        dot.SetShape(pcbnew.SHAPE_T_CIRCLE)
        dot.SetFilled(True)
        dot.SetCenter(pcbnew.VECTOR2I(mm(cx), mm(cy)))
        dot.SetRadius(mm(radius))
        dot.SetLayer(pcbnew.B_SilkS)
        dot.SetWidth(mm(0.10))
        board.Add(dot)

    def add_bsilk_text(label, tx, ty, size=0.80):
        txt = pcbnew.PCB_TEXT(board)
        txt.SetText(label)
        txt.SetPosition(pcbnew.VECTOR2I(mm(tx), mm(ty)))
        txt.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
        txt.SetTextThickness(mm(0.14))
        txt.SetLayer(pcbnew.B_SilkS)
        txt.SetMirrored(True)
        txt.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        txt.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
        board.Add(txt)

    # U1 Pin 1 is at South-East (35.375, 54.863); J1 Pin 1 at (8.760, 63.570)
    add_bsilk_dot(35.80, 56.20, 0.30)
    add_bsilk_text("1", 34.80, 56.80, 0.80)
    add_bsilk_dot(11.28, 63.57, 0.35)
    add_bsilk_text("1", 11.28, 62.10, 0.80)

    for i in range(10):
        add_bsilk_dot(19.050 + 1.625, 20.000 + 8.000 * i - 1.35, 0.22)
    for _, _, _, dx, dy, rot180 in rgb_ring_specs:
        kx = (dx - 1.625) if rot180 else (dx + 1.625)
        add_bsilk_dot(kx, dy - 1.35, 0.22)

    add_bsilk_text("ICIO500 SAT", 24.50, 12.20, 0.80)
    add_bsilk_text("0.8mm 2L", 8.50, 91.50, 0.80)

    # 6. Copper Ground Zones on BOTH F.Cu (EMI shield behind wood/plexi) and B.Cu
    def add_circle_hole(outline, cx, cy, r_mm, n=24):
        outline.NewHole()
        for k in range(n):
            a = 2.0 * math.pi * k / n
            outline.Append(mm(cx + r_mm * math.cos(a)), mm(cy + r_mm * math.sin(a)))

    def make_gnd_zone(layer):
        z = pcbnew.ZONE(board)
        lset = pcbnew.LSET()
        lset.AddLayer(layer)
        z.SetLayerSet(lset)
        z.SetLayer(layer)
        z.SetNet(gnd)
        out = z.Outline()
        out.NewOutline()
        out.Append(mm(X_MIN + 0.30), mm(Y_MIN + 0.30))
        out.Append(mm(X_MAX - 0.30), mm(Y_MIN + 0.30))
        out.Append(mm(X_MAX - 0.30), mm(Y_MAX - 0.30))
        out.Append(mm(X_MIN + 0.30), mm(Y_MAX - 0.30))
        # Optical cutouts around D1..D10 slots
        for i in range(10):
            wy = 20.000 + 8.000 * i
            out.NewHole()
            out.Append(mm(16.30), mm(wy - 1.70))
            out.Append(mm(22.10), mm(wy - 1.70))
            out.Append(mm(22.10), mm(wy + 1.70))
            out.Append(mm(16.30), mm(wy + 1.70))
        # Cutout around encoder M7 bushing & anti-rotation hole
        out.NewHole()
        out.Append(mm(9.50), mm(105.00))
        out.Append(mm(23.50), mm(105.00))
        out.Append(mm(23.50), mm(114.00))
        out.Append(mm(9.50), mm(114.00))
        # Optical cutouts around D11..D16 skirt slots
        for _, _, _, dx, dy, _ in rgb_ring_specs:
            out.NewHole()
            out.Append(mm(dx - 2.00), mm(dy - 1.80))
            out.Append(mm(dx + 2.00), mm(dy - 1.80))
            out.Append(mm(dx + 2.00), mm(dy + 1.80))
            out.Append(mm(dx - 2.00), mm(dy + 1.80))
        # Circular nut/screw keepout holes (R = 2.85 mm) around top M2.5 holes
        for _, mx, my in m25_holes:
            add_circle_hole(out, mx, my, 2.85)
        z.SetMinThickness(mm(0.20))
        z.SetThermalReliefGap(mm(0.25))
        z.SetThermalReliefSpokeWidth(mm(0.25))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        board.Add(z)
        return z

    make_gnd_zone(pcbnew.F_Cu)
    make_gnd_zone(pcbnew.B_Cu)

    board.BuildConnectivity()
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    os.makedirs("kicad", exist_ok=True)
    out_pcb = "kicad/faceplate_satellite.kicad_pcb"
    board.Save(out_pcb)
    print(f"=== BUILD COMPLETE: Saved {out_pcb} cleanly ===")


if __name__ == "__main__":
    run()
