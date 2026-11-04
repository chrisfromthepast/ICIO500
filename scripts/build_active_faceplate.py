import os
import pcbnew
import json

def mm(val):
    return int(val * 1e6)

def run():
    base_path = os.path.join(os.path.dirname(__file__), "..", "elec", "faceplate_base.kicad_pcb")
    with open(base_path, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.split('\n')
    out_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('\t(gr_') or line.startswith('  (gr_'):
            block = [line]
            depth = line.count('(') - line.count(')')
            j = i + 1
            while j < len(lines) and depth > 0:
                block.append(lines[j])
                depth += lines[j].count('(') - lines[j].count(')')
                j += 1
            block_str = '\n'.join(block)
            if 'layer "Edge.Cuts"' in block_str or '(layer "Edge.Cuts")' in block_str:
                i = j
                continue
            else:
                out_lines.extend(block)
                i = j
                continue
        else:
            out_lines.append(line)
            i += 1

    clean_text = '\n'.join(out_lines)

    edge_cuts_sexpr = """
\t(gr_line
\t\t(start 0 0)
\t\t(end 38.1 0)
\t\t(stroke
\t\t\t(width 0.1)
\t\t\t(type default)
\t\t)
\t\t(layer "Edge.Cuts")
\t\t(uuid "outline-top-0001")
\t)
\t(gr_line
\t\t(start 38.1 0)
\t\t(end 38.1 133.35)
\t\t(stroke
\t\t\t(width 0.1)
\t\t\t(type default)
\t\t)
\t\t(layer "Edge.Cuts")
\t\t(uuid "outline-right-0002")
\t)
\t(gr_line
\t\t(start 38.1 133.35)
\t\t(end 0 133.35)
\t\t(stroke
\t\t\t(width 0.1)
\t\t\t(type default)
\t\t)
\t\t(layer "Edge.Cuts")
\t\t(uuid "outline-bottom-0003")
\t)
\t(gr_line
\t\t(start 0 133.35)
\t\t(end 0 0)
\t\t(stroke
\t\t\t(width 0.1)
\t\t\t(type default)
\t\t)
\t\t(layer "Edge.Cuts")
\t\t(uuid "outline-left-0004")
\t)
\t(gr_circle
\t\t(center 19.05 109.35)
\t\t(end 22.65 109.35)
\t\t(stroke
\t\t\t(width 0.1)
\t\t\t(type default)
\t\t)
\t\t(fill no)
\t\t(layer "Edge.Cuts")
\t\t(uuid "encoder-hole-m7")
\t)
\t(gr_circle
\t\t(center 11.55 109.35)
\t\t(end 12.65 109.35)
\t\t(stroke
\t\t\t(width 0.1)
\t\t\t(type default)
\t\t)
\t\t(fill no)
\t\t(layer "Edge.Cuts")
\t\t(uuid "encoder-antirotation-pin")
\t)
"""
    last_paren = clean_text.rfind(')')
    prepared_text = clean_text[:last_paren] + edge_cuts_sexpr + clean_text[last_paren:]

    with open("temp_perfect_base.kicad_pcb", "w", encoding="utf-8") as f:
        f.write(prepared_text)

    board = pcbnew.LoadBoard("temp_perfect_base.kicad_pcb")

    def get_or_create_net(name):
        net = board.FindNet(name)
        if not net:
            net = pcbnew.NETINFO_ITEM(board, name)
            board.Add(net)
        return net

    gnd = get_or_create_net('GND')
    pwr = get_or_create_net('+3V3')
    pwr_in = get_or_create_net('+3V3_IN')
    pwr_in_mid = get_or_create_net('+3V3_IN_MID')
    pwr_in_jump = get_or_create_net('+3V3_IN_JUMP')
    sda_in = get_or_create_net('SDA_IN')
    sda = get_or_create_net('SDA')
    scl = get_or_create_net('SCL')
    enc_a = get_or_create_net('ENC_A')
    enc_b = get_or_create_net('ENC_B')
    enc_sw = get_or_create_net('ENC_SW')

    led_nets = [get_or_create_net(f'LED_{i+1}') for i in range(10)]
    led_mid_nets = [get_or_create_net(f'Net-(D{i+1}-Pad2)') for i in range(10)]

    lib_base = r"C:\Program Files\KiCad\10.0\share\kicad\footprints"
    def load_fp(pretty_lib, fp_name, ref):
        fp = pcbnew.FootprintLoad(os.path.join(lib_base, pretty_lib), fp_name)
        fp.SetReference(ref)
        return fp

    # J1 at (11.280, 75.000) on B.Cu
    j1 = load_fp("Connector_PinSocket_2.54mm.pretty", "PinSocket_2x10_P2.54mm_Vertical_SMD", "J1")
    j1.SetValue('Conn_02x10_Odd_Even')
    j1.SetPosition(pcbnew.VECTOR2I(mm(11.280), mm(75.000)))
    j1.Reference().SetVisible(False)
    for g in j1.GraphicalItems():
        if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
            g.SetLayer(pcbnew.Dwgs_User)
    board.Add(j1)
    j1.Flip(j1.GetPosition(), False)

    j1_map = {
        '1': gnd, '2': pwr_in_jump, '3': sda_in, '4': gnd, '5': scl, '6': gnd,
        '7': gnd, '8': gnd, '9': enc_b, '10': enc_a, '11': gnd, '12': enc_sw,
        '13': gnd, '14': gnd, '15': gnd, '16': gnd, '17': gnd, '18': gnd,
        '19': gnd, '20': gnd
    }
    for pad in j1.Pads():
        pad.SetNet(j1_map.get(str(pad.GetNumber()), gnd))

    # J2 at (19.050, 121.850) on B.Cu
    j2 = load_fp("Connector_PinSocket_2.54mm.pretty", "PinSocket_1x05_P2.54mm_Vertical_SMD_Pin1Left", "J2")
    j2.SetValue('Conn_01x05_Female')
    j2.SetPosition(pcbnew.VECTOR2I(mm(19.050), mm(121.850)))
    j2.SetOrientation(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
    j2.Reference().SetVisible(False)
    for g in j2.GraphicalItems():
        if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
            g.SetLayer(pcbnew.Dwgs_User)
    board.Add(j2)
    j2.Flip(j2.GetPosition(), False)
    j2_map = {'1': enc_a, '2': gnd, '3': enc_b, '4': enc_sw, '5': gnd}
    for p in j2.Pads():
        if str(p.GetNumber()) in j2_map:
            p.SetNet(j2_map[str(p.GetNumber())])

    # 10 LEDs D1..D10 centered at (19.050, wy) on B.Cu
    for i in range(10):
        wy = 20.000 + 8.000 * i
        d = load_fp("LED_SMD.pretty", "LED_0805_2012Metric", f"D{i+1}")
        d.SetPosition(pcbnew.VECTOR2I(mm(19.050), mm(wy)))
        board.Add(d)
        d.Flip(d.GetPosition(), False)
        d.Reference().SetVisible(False)
        for g in d.GraphicalItems():
            if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
                g.SetLayer(pcbnew.Dwgs_User)
        for p in d.Pads():
            if str(p.GetNumber()) == '1':
                p.SetNet(led_mid_nets[i])
            else:
                p.SetNet(gnd)

    # 10 Resistors R1..R10 placed at (27.000, wy) in the East corridor
    for i in range(10):
        wy = 20.000 + 8.000 * i
        r = load_fp("Resistor_SMD.pretty", "R_0402_1005Metric", f"R{i+1}")
        r.SetPosition(pcbnew.VECTOR2I(mm(27.000), mm(wy)))
        r.SetOrientation(pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))
        r.Reference().SetVisible(False)
        for g in r.GraphicalItems():
            if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
                g.SetLayer(pcbnew.Dwgs_User)
        board.Add(r)
        r.Flip(r.GetPosition(), False)
        for p in r.Pads():
            if str(p.GetNumber()) == '1':
                p.SetNet(led_mid_nets[i])
            else:
                p.SetNet(led_nets[i])

    # U1 (TSSOP-24) at (32.500, 16.000) on B.Cu, orientation 90 deg
    u1 = load_fp("Package_SO.pretty", "TSSOP-24_4.4x7.8mm_P0.65mm", "U1")
    u1.SetPosition(pcbnew.VECTOR2I(mm(32.500), mm(16.000)))
    u1.SetOrientation(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
    u1.Reference().SetVisible(False)
    for g in u1.GraphicalItems():
        if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
            g.SetLayer(pcbnew.Dwgs_User)
    board.Add(u1)
    u1.Flip(u1.GetPosition(), False)

    u1_map = {
        '11': led_nets[0], '10': led_nets[1], '9': led_nets[2], '8': led_nets[3],
        '7':  led_nets[4], '6':  led_nets[5], '5': led_nets[6], '4': led_nets[7],
        '3':  led_nets[8], '2':  led_nets[9], '12': gnd, '1': gnd,
        '24': pwr, '23': sda, '22': scl, '21': gnd, '20': gnd,
        '19': gnd, '18': gnd, '17': gnd, '16': gnd, '15': gnd,
        '14': gnd, '13': gnd,
    }
    for pad in u1.Pads():
        num = str(pad.GetNumber())
        if num in u1_map:
            pad.SetNet(u1_map[num])

    # Passives:
    # FB1: L_0402_1005Metric vertical orientation 270 deg at (36.800, 2.800)
    # Pad 1 (+3V3_IN) at North (36.800, 2.315), Pad 2 (+3V3) at South (36.800, 3.285)
    fb1 = load_fp("Inductor_SMD.pretty", "L_0402_1005Metric", "FB1")
    fb1.SetPosition(pcbnew.VECTOR2I(mm(36.800), mm(2.800)))
    fb1.SetOrientation(pcbnew.EDA_ANGLE(270, pcbnew.DEGREES_T))
    fb1.Reference().SetVisible(False)
    for g in fb1.GraphicalItems():
        if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
            g.SetLayer(pcbnew.Dwgs_User)
    board.Add(fb1)
    fb1.Flip(fb1.GetPosition(), False)
    for p in fb1.Pads():
        p.SetNet(pwr_in if str(p.GetNumber()) == '1' else pwr)

    # C1 (bypass cap 0.1uF for +3V3): C_0402_1005Metric horizontal at (36.800, 4.200)
    # Pad 1 (+3V3) at West (36.320, 4.200), Pad 2 (GND) at East (37.280, 4.200)
    c1 = load_fp("Capacitor_SMD.pretty", "C_0402_1005Metric", "C1")
    c1.SetPosition(pcbnew.VECTOR2I(mm(36.800), mm(4.200)))
    c1.Reference().SetVisible(False)
    for g in c1.GraphicalItems():
        if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
            g.SetLayer(pcbnew.Dwgs_User)
    board.Add(c1)
    c1.Flip(c1.GetPosition(), False)
    c1.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
    for p in c1.Pads():
        p.SetNet(pwr if str(p.GetNumber()) == '1' else gnd)

    # C2 (bulk bypass 10uF for +3V3): C_0402_1005Metric horizontal at (36.800, 5.400)
    # Pad 1 (+3V3) at West (36.320, 5.400), Pad 2 (GND) at East (37.280, 5.400)
    c2 = load_fp("Capacitor_SMD.pretty", "C_0402_1005Metric", "C2")
    c2.SetPosition(pcbnew.VECTOR2I(mm(36.800), mm(5.400)))
    c2.Reference().SetVisible(False)
    for g in c2.GraphicalItems():
        if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
            g.SetLayer(pcbnew.Dwgs_User)
    board.Add(c2)
    c2.Flip(c2.GetPosition(), False)
    c2.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
    for p in c2.Pads():
        p.SetNet(pwr if str(p.GetNumber()) == '1' else gnd)

    # R11 (SDA pullup to +3V3): R_0402_1005Metric horizontal at (36.200, 8.800)
    # Orientation 180 deg: Pad 2 (SDA) at West (35.690, 8.800), Pad 1 (+3V3) at East (36.710, 8.800)
    r11 = load_fp("Resistor_SMD.pretty", "R_0402_1005Metric", "R11")
    r11.SetPosition(pcbnew.VECTOR2I(mm(36.200), mm(8.800)))
    r11.Reference().SetVisible(False)
    for g in r11.GraphicalItems():
        if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
            g.SetLayer(pcbnew.Dwgs_User)
    board.Add(r11)
    r11.Flip(r11.GetPosition(), False)
    r11.SetOrientation(pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))
    for p in r11.Pads():
        p.SetNet(pwr if str(p.GetNumber()) == '1' else sda)

    # R12 (SCL pullup to +3V3): R_0805_2012Metric horizontal straddling SDA at (35.425, 10.600)
    # Pad 1 (SCL) at West (34.513, 10.600), Pad 2 (+3V3) at East (36.337, 10.600)
    r12 = load_fp("Resistor_SMD.pretty", "R_0805_2012Metric", "R12")
    r12.SetPosition(pcbnew.VECTOR2I(mm(35.425), mm(10.600)))
    r12.Reference().SetVisible(False)
    for g in r12.GraphicalItems():
        if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
            g.SetLayer(pcbnew.Dwgs_User)
    board.Add(r12)
    r12.Flip(r12.GetPosition(), False)
    r12.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
    for p in r12.Pads():
        if p.GetPosition().x / 1e6 < 35.425:
            p.SetNet(scl)
        else:
            p.SetNet(pwr)

    # Jumpers in West Corridor:
    # R13 (0805 0R Jumper for SDA bridging over SCL at J1 exit):
    r13 = load_fp("Resistor_SMD.pretty", "R_0805_2012Metric", "R13")
    r13.SetValue("0R")
    r13.SetPosition(pcbnew.VECTOR2I(mm(4.000), mm(66.110)))
    r13.Reference().SetVisible(False)
    for g in r13.GraphicalItems():
        if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
            g.SetLayer(pcbnew.Dwgs_User)
    board.Add(r13)
    r13.Flip(r13.GetPosition(), False)
    for p in r13.Pads():
        if p.GetPosition().x / 1e6 > 4.000:
            p.SetNet(sda_in)
        else:
            p.SetNet(sda)

    # R14 (0805 0R Jumper for +3V3_IN bridging over SCL at X=4.000):
    r14 = load_fp("Resistor_SMD.pretty", "R_0805_2012Metric", "R14")
    r14.SetValue("0R")
    r14.SetPosition(pcbnew.VECTOR2I(mm(4.000), mm(62.400)))
    r14.Reference().SetVisible(False)
    for g in r14.GraphicalItems():
        if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
            g.SetLayer(pcbnew.Dwgs_User)
    board.Add(r14)
    r14.Flip(r14.GetPosition(), False)
    for p in r14.Pads():
        if p.GetPosition().x / 1e6 > 4.000:
            p.SetNet(pwr_in_jump)
        else:
            p.SetNet(pwr_in_mid)

    # R15 (0805 0R Jumper for +3V3_IN bridging over SDA at X=2.000):
    r15 = load_fp("Resistor_SMD.pretty", "R_0805_2012Metric", "R15")
    r15.SetValue("0R")
    r15.SetPosition(pcbnew.VECTOR2I(mm(2.000), mm(58.000)))
    r15.Reference().SetVisible(False)
    for g in r15.GraphicalItems():
        if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
            g.SetLayer(pcbnew.Dwgs_User)
    board.Add(r15)
    r15.Flip(r15.GetPosition(), False)
    for p in r15.Pads():
        if p.GetPosition().x / 1e6 > 2.000:
            p.SetNet(pwr_in_mid)
        else:
            p.SetNet(pwr_in)

    print("=== STEP 3: ROUTE PLANAR TRACKS ON B.CU ===")
    def track(x1, y1, x2, y2, net, width=0.20):
        if abs(x1-x2) < 1e-4 and abs(y1-y2) < 1e-4:
            return None
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
        t.SetWidth(mm(width))
        t.SetLayer(pcbnew.B_Cu)
        t.SetNet(net)
        board.Add(t)
        return t

    # 1. Direct Resistor to LED tracks:
    for i in range(10):
        wy = 20.000 + 8.000 * i
        track(26.490, wy, 19.988, wy, led_mid_nets[i])

    # 2. 10 Planar Non-Crossing L-shape LED Tracks from U1 to R1..R10:
    u1_led_x = [29.575, 30.225, 30.875, 31.525, 32.175, 32.825, 33.475, 34.125, 34.775, 35.425]
    for i in range(10):
        ux = u1_led_x[i]
        wy = 20.000 + 8.000 * i
        net = led_nets[i]
        track(ux, 18.863, ux, wy, net)
        track(ux, wy, 27.510, wy, net)

    # 3. Concentric Non-Crossing Control & Power Routing:
    # Top highway: SDA at Y=6.400, SCL at Y=7.400 (both strictly below MH1 keepout 6.06!)
    # SDA: from J1 Pad 3 (8.760, 66.110) west to R13, then north along X=2.000:
    r13_p1 = [p for p in r13.Pads() if p.GetPosition().x/1e6 > 4.000][0]
    r13_p2 = [p for p in r13.Pads() if p.GetPosition().x/1e6 < 4.000][0]
    track(8.760, 66.110, r13_p1.GetPosition().x/1e6, 66.110, sda_in)
    track(r13_p2.GetPosition().x/1e6, 66.110, 2.000, 66.110, sda)
    track(2.000, 66.110, 2.000, 6.400, sda)
    track(2.000, 6.400, 35.425, 6.400, sda)
    track(35.425, 6.400, 35.425, 13.138, sda) # Enters U1 Pin 23, passing through R12 center at Y=10.600!
    # Stub to R11 Pad 2 at (35.690, 8.800):
    r11_p2 = [p for p in r11.Pads() if str(p.GetNumber()) == '2'][0]
    track(35.425, 8.800, r11_p2.GetPosition().x/1e6, 8.800, sda)

    # SCL: J1 Pad 5 (8.760, 68.650) -> west to X=4.000 -> north along X=4.000 to Y=7.400:
    track(8.760, 68.650, 4.000, 68.650, scl)
    track(4.000, 68.650, 4.000, 7.400, scl)
    track(4.000, 7.400, 34.775, 7.400, scl)
    track(34.775, 7.400, 34.775, 13.138, scl) # Enters U1 Pad 22 at (34.775, 13.138)
    # Stub to R12 Pad 1 at (34.513, 10.600):
    r12_p1 = [p for p in r12.Pads() if p.GetPosition().x/1e6 < 35.425][0]
    track(34.775, 10.600, r12_p1.GetPosition().x/1e6, 10.600, scl)

    # +3V3_IN_JUMP: from J1 Pad 2 (13.800, 63.570):
    r14_p1 = [p for p in r14.Pads() if p.GetPosition().x/1e6 > 4.000][0]
    r14_p2 = [p for p in r14.Pads() if p.GetPosition().x/1e6 < 4.000][0]
    track(13.800, 63.570, 13.800, 62.400, pwr_in_jump)
    track(13.800, 62.400, r14_p1.GetPosition().x/1e6, 62.400, pwr_in_jump)

    # +3V3_IN_MID: from R14 Pad 2 (3.088, 62.400) to R15 Pad 1 (2.912, 58.000):
    r15_p1 = [p for p in r15.Pads() if p.GetPosition().x/1e6 > 2.000][0]
    r15_p2 = [p for p in r15.Pads() if p.GetPosition().x/1e6 < 2.000][0]
    track(r14_p2.GetPosition().x/1e6, 62.400, 2.500, 62.400, pwr_in_mid)
    track(2.500, 62.400, 2.500, 58.000, pwr_in_mid)
    track(2.500, 58.000, r15_p1.GetPosition().x/1e6, 58.000, pwr_in_mid)

    # +3V3_IN: from R15 Pad 2 (1.088, 58.000) west to X=1.000, north along X=1.000 to Y=1.100:
    track(r15_p2.GetPosition().x/1e6, 58.000, 1.000, 58.000, pwr_in)
    track(1.000, 58.000, 1.000, 1.100, pwr_in)
    # Along Y=1.100 across top of board (completely above MH1!) to X=36.800:
    fb1_p1 = [p for p in fb1.Pads() if str(p.GetNumber()) == '1'][0]
    fb1_p2 = [p for p in fb1.Pads() if str(p.GetNumber()) == '2'][0]
    track(1.000, 1.100, 36.800, 1.100, pwr_in)
    track(36.800, 1.100, 36.800, fb1_p1.GetPosition().y/1e6, pwr_in)

    # +3V3 Power distribution from FB1 Pad 2 at (36.800, 3.285):
    # Spine along X=36.330 from Y=3.285 down to Y=12.500:
    track(36.800, fb1_p2.GetPosition().y/1e6, 36.330, fb1_p2.GetPosition().y/1e6, pwr)
    track(36.330, fb1_p2.GetPosition().y/1e6, 36.330, 12.500, pwr)
    # Stubs to +3V3 pads:
    # C1 Pad 1 at (36.320, 4.200):
    c1_p1 = [p for p in c1.Pads() if str(p.GetNumber()) == '1'][0]
    track(36.330, 4.200, c1_p1.GetPosition().x/1e6, 4.200, pwr)
    # C2 Pad 1 at (36.320, 5.400):
    c2_p1 = [p for p in c2.Pads() if str(p.GetNumber()) == '1'][0]
    track(36.330, 5.400, c2_p1.GetPosition().x/1e6, 5.400, pwr)
    # R11 Pad 1 at (36.710, 8.800):
    r11_p1 = [p for p in r11.Pads() if str(p.GetNumber()) == '1'][0]
    track(36.330, 8.800, r11_p1.GetPosition().x/1e6, 8.800, pwr)
    # R12 Pad 2 at (36.337, 10.600):
    r12_p2 = [p for p in r12.Pads() if p.GetPosition().x/1e6 > 35.425][0]
    track(36.330, 10.600, r12_p2.GetPosition().x/1e6, 10.600, pwr)
    # Feed U1 Pad 24 at (36.075, 13.138):
    track(36.330, 12.500, 36.075, 12.500, pwr)
    track(36.075, 12.500, 36.075, 13.138, pwr)

    # 4. Encoder Routing:
    track(13.800, 76.270, 11.280, 76.270, enc_sw)
    track(11.280, 76.270, 11.280, 88.000, enc_sw)
    track(11.280, 88.000, 3.800, 88.000, enc_sw)
    track(3.800, 88.000, 3.800, 117.000, enc_sw)
    track(3.800, 117.000, 16.510, 117.000, enc_sw)
    track(16.510, 117.000, 16.510, 120.200, enc_sw)

    track(8.760, 73.730, 2.800, 73.730, enc_b)
    track(2.800, 73.730, 2.800, 125.000, enc_b)
    track(2.800, 125.000, 19.050, 125.000, enc_b)
    track(19.050, 125.000, 19.050, 123.500, enc_b)

    track(13.800, 73.730, 16.000, 73.730, enc_a)
    track(16.000, 73.730, 16.000, 96.000, enc_a)
    track(16.000, 96.000, 24.130, 96.000, enc_a)
    track(24.130, 96.000, 24.130, 123.500, enc_a)

    # 5. Ground Connections:
    track(21.590, 120.200, 21.590, 118.000, gnd)
    track(13.970, 123.500, 12.000, 123.500, gnd)

    # U1 North GND rail: Pins 13..21
    track(27.500, 13.138, 34.125, 13.138, gnd)
    # Connect U1 North GND to South GND via West corridor of U1:
    track(27.500, 13.138, 27.500, 18.863, gnd)
    track(27.500, 18.863, 28.925, 18.863, gnd) # Ties into Pin 12 GND!

    # East ground spine connecting C1 Pad 2 (37.280, 4.200) and C2 Pad 2 (37.280, 5.400) to main ground:
    c1_p2 = [p for p in c1.Pads() if str(p.GetNumber()) == '2'][0]
    c2_p2 = [p for p in c2.Pads() if str(p.GetNumber()) == '2'][0]
    track(c1_p2.GetPosition().x/1e6, 4.200, 37.280, 4.200, gnd)
    track(c2_p2.GetPosition().x/1e6, 5.400, 37.280, 5.400, gnd)
    track(37.280, 4.200, 37.280, 18.863, gnd)
    track(37.280, 18.863, 36.075, 18.863, gnd) # Ties into U1 South Pin 1 GND!

    # LED Ground spine:
    for k in range(9):
        wy_a = 20.000 + 8.000 * k
        wy_b = 20.000 + 8.000 * (k + 1)
        track(18.113, wy_a, 18.113, wy_b, gnd)

    track(13.800, 68.650, 18.113, 68.650, gnd)

    # Step 4: Copper Zones
    W, H = 38.10, 133.35

    # Front Zone: Cosmetic Floating Copper Shield on F.Cu
    zone_f = pcbnew.ZONE(board)
    lset_f = pcbnew.LSET()
    lset_f.AddLayer(pcbnew.F_Cu)
    zone_f.SetLayerSet(lset_f)
    zone_f.SetLayer(pcbnew.F_Cu)
    zone_f.SetNetCode(0)
    out_f = zone_f.Outline()
    out_f.NewOutline()
    out_f.Append(mm(0.5), mm(0.5))
    out_f.Append(mm(W-0.5), mm(0.5))
    out_f.Append(mm(W-0.5), mm(H-0.5))
    out_f.Append(mm(0.5), mm(H-0.5))
    for i in range(10):
        wy = 20.000 + 8.000 * i
        wx1, wx2 = 13.05, 25.05
        wy1, wy2 = wy - 2.0, wy + 2.0
        out_f.NewHole()
        out_f.Append(mm(wx1), mm(wy1))
        out_f.Append(mm(wx2), mm(wy1))
        out_f.Append(mm(wx2), mm(wy2))
        out_f.Append(mm(wx1), mm(wy2))
    zone_f.SetMinThickness(mm(0.20))
    zone_f.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    board.Add(zone_f)

    # Rear Zone: GND Copper Zone on B.Cu covering the circuit area
    zone_b = pcbnew.ZONE(board)
    lset_b = pcbnew.LSET()
    lset_b.AddLayer(pcbnew.B_Cu)
    zone_b.SetLayerSet(lset_b)
    zone_b.SetLayer(pcbnew.B_Cu)
    zone_b.SetNet(gnd)
    out_b = zone_b.Outline()
    out_b.NewOutline()
    out_b.Append(mm(0.5), mm(13.0)) # Starts below North routing highway!
    out_b.Append(mm(W-0.5), mm(13.0))
    out_b.Append(mm(W-0.5), mm(H-0.5))
    out_b.Append(mm(0.5), mm(H-0.5))
    for i in range(10):
        wy = 20.000 + 8.000 * i
        wx1, wx2 = 13.05, 25.05
        wy1, wy2 = wy - 2.0, wy + 2.0
        out_b.NewHole()
        out_b.Append(mm(wx1), mm(wy1))
        out_b.Append(mm(wx2), mm(wy1))
        out_b.Append(mm(wx2), mm(wy2))
        out_b.Append(mm(wx1), mm(wy2))
    zone_b.SetMinThickness(mm(0.20))
    zone_b.SetThermalReliefGap(mm(0.25))
    zone_b.SetThermalReliefSpokeWidth(mm(0.25))
    zone_b.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    board.Add(zone_b)

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    output_path = "build/icio500/faceplate_front.kicad_pcb"
    board.Save(output_path)
    if os.path.exists("temp_perfect_base.kicad_pcb"):
        try:
            os.remove("temp_perfect_base.kicad_pcb")
        except OSError:
            pass
    print(f"=== BUILD COMPLETE: Saved {output_path} successfully! ===")

if __name__ == '__main__':
    run()
