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
            if 'layer "Edge.Cuts"' in block_str or '(layer "Edge.Cuts")' in block_str or \
               'layer "B.Mask"' in block_str or '(layer "B.Mask")' in block_str:
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
    board.SetCopperLayerCount(2)
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(mm(2.0))
    ds.m_CopperEdgeClearance = mm(0.25)
    ds.m_HoleClearance = mm(0.20)

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

    led_nets = [get_or_create_net(f'LED_{i+1}') for i in range(10)]
    led_mid_nets = [get_or_create_net(f'Net-(D{i+1}-Pad2)') for i in range(10)]

    rgb_nets = {
        'R': get_or_create_net('RGB_R'),
        'G': get_or_create_net('RGB_G'),
        'B': get_or_create_net('RGB_B'),
    }
    rgb_r_south = get_or_create_net('RGB_R_SOUTH')
    rgb_g_west = get_or_create_net('RGB_G_WEST')
    rgb_b_north = get_or_create_net('RGB_B_NORTH')
    rgb_b_west = get_or_create_net('RGB_B_WEST')
    rgb_mid_nets = [get_or_create_net(f'Net-(D{11+i}-Pad1)') for i in range(6)]

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
        '7': gnd, '8': gnd, '9': gnd, '10': gnd, '11': gnd, '12': gnd,
        '13': gnd, '14': gnd, '15': gnd, '16': gnd, '17': gnd, '18': gnd,
        '19': gnd, '20': gnd
    }
    for pad in j1.Pads():
        pad.SetNet(j1_map.get(str(pad.GetNumber()), gnd))

    # BR1 at (10.310, 14.525) on B.Cu (Würth WP-SMRA-M3, mates with carrier MH1)
    br1 = load_fp("Mounting_Wuerth.pretty", "Mounting_Wuerth_WP-SMRA-M3_L7mm_7466303_Horizontal", "BR1")
    br1.SetValue("WP-SMRA-M3")
    br1.SetPosition(pcbnew.VECTOR2I(mm(10.310), mm(14.525)))
    board.Add(br1)
    br1.Flip(br1.GetPosition(), False)
    br1.Reference().SetVisible(False)
    for g in br1.GraphicalItems():
        if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
            g.SetLayer(pcbnew.Dwgs_User)
    for p in br1.Pads():
        p.SetNet(gnd)

    # BR2 at (10.310, 118.825) on B.Cu (Würth WP-SMRA-M3, mates with carrier MH2)
    br2 = load_fp("Mounting_Wuerth.pretty", "Mounting_Wuerth_WP-SMRA-M3_L7mm_7466303_Horizontal", "BR2")
    br2.SetValue("WP-SMRA-M3")
    br2.SetPosition(pcbnew.VECTOR2I(mm(10.310), mm(118.825)))
    board.Add(br2)
    br2.Flip(br2.GetPosition(), False)
    br2.Reference().SetVisible(False)
    for g in br2.GraphicalItems():
        if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
            g.SetLayer(pcbnew.Dwgs_User)
    for p in br2.Pads():
        p.SetNet(gnd)

    def tune_rev_led_pads(fp, remove_npth=False):
        to_remove = []
        for p in fp.Pads():
            if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                if remove_npth:
                    to_remove.append(p)
                else:
                    p.SetSize(pcbnew.VECTOR2I(mm(1.92), mm(1.68)))
                    p.SetDrillSize(pcbnew.VECTOR2I(mm(1.92), mm(1.68)))
            elif str(p.GetNumber()) == '1':
                p.SetPos(pcbnew.VECTOR2I(mm(-1.625), 0))
                if remove_npth:
                    p.SetSize(pcbnew.VECTOR2I(mm(0.85), mm(1.60)))
                else:
                    p.SetSize(pcbnew.VECTOR2I(mm(0.80), mm(1.60)))
            elif str(p.GetNumber()) == '2':
                p.SetPos(pcbnew.VECTOR2I(mm(1.625), 0))
                if remove_npth:
                    p.SetSize(pcbnew.VECTOR2I(mm(0.85), mm(1.60)))
                else:
                    p.SetSize(pcbnew.VECTOR2I(mm(0.80), mm(1.60)))
        for p in to_remove:
            fp.Remove(p)

    # 10 Reverse-Mount Gull-Wing 1206 LEDs D1..D10 centered at (19.050, wy) on B.Cu
    # Mounted over 2.00 x 1.80 mm bottom blind-milled pockets (NO front holes)
    for i in range(10):
        wy = 20.000 + 8.000 * i
        d = load_fp("LED_SMD.pretty", "LED_1206_3216Metric_ReverseMount_Hole1.8x2.4mm", f"D{i+1}")
        tune_rev_led_pads(d, remove_npth=True)
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
            elif str(p.GetNumber()) == '2':
                p.SetNet(pwr)

    # 10 Resistors R1..R10 placed at (25.200, wy) in the East corridor (clears U1 courtyard & nested loops)
    # Staggered values for brightness balancing: 68R (Red), 82R (Yellow), 100R (Green)
    for i in range(10):
        wy = 20.000 + 8.000 * i
        r = load_fp("Resistor_SMD.pretty", "R_0402_1005Metric", f"R{i+1}")
        if i == 0:
            r.SetValue("68R")
        elif i in (1, 2):
            r.SetValue("82R")
        else:
            r.SetValue("100R")
        r.SetPosition(pcbnew.VECTOR2I(mm(25.200), mm(wy)))
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

    # 6-LED RGBRGB Ring D11..D16 at R=10.0 mm around encoder (19.050, 109.350) + R16..R21 (100R)
    # Through-slots (1.92 x 1.68 mm NPTH) under knob skirt.
    # Channels: P1_2=RGB_R (D11, D14), P1_3=RGB_G (D12, D15), P1_4=RGB_B (D13, D16)
    # D11..D14 have Anode (Pad 2) left/inside, Cathode (Pad 1) right/outside.
    # D15..D16 are rotated 180 deg before Flip so Anode (Pad 2) faces right/inside and Cathode (Pad 1) faces left/outside.
    rgb_ring_specs = [
        (11, 16, 'R', 19.050,  99.350, False),  # 270 deg (12 o'clock)
        (12, 17, 'G', 27.710, 104.350, False),  # 330 deg (2 o'clock)
        (13, 18, 'B', 27.710, 114.350, False),  #  30 deg (4 o'clock)
        (14, 19, 'R', 19.050, 119.350, False),  #  90 deg (6 o'clock)
        (15, 20, 'G', 10.390, 114.350, True),   # 150 deg (8 o'clock)
        (16, 21, 'B', 10.390, 104.350, True),   # 210 deg (10 o'clock)
    ]
    for idx, (d_num, r_num, ch, dx, dy, rot180) in enumerate(rgb_ring_specs):
        d = load_fp("LED_SMD.pretty", "LED_1206_3216Metric_ReverseMount_Hole1.8x2.4mm", f"D{d_num}")
        tune_rev_led_pads(d, remove_npth=False)
        d.SetPosition(pcbnew.VECTOR2I(mm(dx), mm(dy)))
        if rot180:
            d.SetOrientation(pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))
        board.Add(d)
        d.Flip(d.GetPosition(), False)
        d.Reference().SetVisible(False)
        for g in d.GraphicalItems():
            if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
                g.SetLayer(pcbnew.Dwgs_User)
        for p in d.Pads():
            if str(p.GetNumber()) == '1':
                p.SetNet(rgb_mid_nets[idx])
            elif str(p.GetNumber()) == '2':
                p.SetNet(pwr)

        r = load_fp("Resistor_SMD.pretty", "R_0402_1005Metric", f"R{r_num}")
        r.SetValue("100R")
        rx = (dx - 3.400) if rot180 else (dx + 3.400)
        r.SetPosition(pcbnew.VECTOR2I(mm(rx), mm(dy)))
        if rot180:
            r.SetOrientation(pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))
        r.Reference().SetVisible(False)
        for g in r.GraphicalItems():
            if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
                g.SetLayer(pcbnew.Dwgs_User)
        board.Add(r)
        r.Flip(r.GetPosition(), False)
        if r_num == 16:
            r_net = rgb_r_south
        elif r_num == 19:
            r_net = rgb_nets['R']
        elif r_num == 20:
            r_net = rgb_g_west
        elif r_num == 21:
            r_net = rgb_b_west
        else:
            r_net = rgb_nets[ch]
        for p in r.Pads():
            if str(p.GetNumber()) == '1':
                p.SetNet(r_net)
            else:
                p.SetNet(rgb_mid_nets[idx])

    # U1 (TSSOP-24) shifted 2.000 mm West to (30.500, 16.000) on B.Cu, orientation 90 deg
    u1 = load_fp("Package_SO.pretty", "TSSOP-24_4.4x7.8mm_P0.65mm", "U1")
    u1.SetPosition(pcbnew.VECTOR2I(mm(30.500), mm(16.000)))
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
        '3':  gnd,         '2':  gnd,         '1': gnd,         '12': gnd,
        '13': led_nets[8], '14': led_nets[9],
        '15': rgb_nets['G'], '16': rgb_nets['B'], '17': rgb_nets['R'],
        '18': gnd,         '19': gnd,         '20': gnd,
        '21': gnd,         '22': scl,         '23': sda,        '24': pwr,
    }
    for pad in u1.Pads():
        num = str(pad.GetNumber())
        if num in u1_map:
            pad.SetNet(u1_map[num])
            if pad.GetNetname() == 'GND':
                pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)

    # Passives:
    # FB1: L_0402_1005Metric vertical orientation 270 deg at (36.800, 2.800)
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

    # R11 (SDA pullup to +3V3): R_0402_1005Metric horizontal at (34.200, 8.800)
    r11 = load_fp("Resistor_SMD.pretty", "R_0402_1005Metric", "R11")
    r11.SetPosition(pcbnew.VECTOR2I(mm(34.200), mm(8.800)))
    r11.Reference().SetVisible(False)
    for g in r11.GraphicalItems():
        if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
            g.SetLayer(pcbnew.Dwgs_User)
    board.Add(r11)
    r11.Flip(r11.GetPosition(), False)
    r11.SetOrientation(pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))
    for p in r11.Pads():
        p.SetNet(pwr if str(p.GetNumber()) == '1' else sda)

    # R12 (SCL pullup to +3V3): R_0805_2012Metric horizontal straddling SDA at (33.425, 10.600)
    r12 = load_fp("Resistor_SMD.pretty", "R_0805_2012Metric", "R12")
    r12.SetPosition(pcbnew.VECTOR2I(mm(33.425), mm(10.600)))
    r12.Reference().SetVisible(False)
    for g in r12.GraphicalItems():
        if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
            g.SetLayer(pcbnew.Dwgs_User)
    board.Add(r12)
    r12.Flip(r12.GetPosition(), False)
    r12.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
    for p in r12.Pads():
        if p.GetPosition().x / 1e6 < 33.425:
            p.SetNet(scl)
        else:
            p.SetNet(pwr)

    # Jumpers in West Corridor (R13, R14 shifted to X=4.500 for >= 0.575 mm clearance to SDA at 2.400):
    # R13 (0805 0R Jumper for SDA bridging over SCL at J1 exit):
    r13 = load_fp("Resistor_SMD.pretty", "R_0805_2012Metric", "R13")
    r13.SetValue("0R")
    r13.SetPosition(pcbnew.VECTOR2I(mm(4.500), mm(66.110)))
    r13.Reference().SetVisible(False)
    for g in r13.GraphicalItems():
        if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
            g.SetLayer(pcbnew.Dwgs_User)
    board.Add(r13)
    r13.Flip(r13.GetPosition(), False)
    for p in r13.Pads():
        if p.GetPosition().x / 1e6 > 4.500:
            p.SetNet(sda_in)
        else:
            p.SetNet(sda)

    # R14 (0805 0R Jumper for +3V3_IN bridging over SCL at X=4.500):
    r14 = load_fp("Resistor_SMD.pretty", "R_0805_2012Metric", "R14")
    r14.SetValue("0R")
    r14.SetPosition(pcbnew.VECTOR2I(mm(4.500), mm(62.400)))
    r14.Reference().SetVisible(False)
    for g in r14.GraphicalItems():
        if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
            g.SetLayer(pcbnew.Dwgs_User)
    board.Add(r14)
    r14.Flip(r14.GetPosition(), False)
    for p in r14.Pads():
        if p.GetPosition().x / 1e6 > 4.500:
            p.SetNet(pwr_in_jump)
        else:
            p.SetNet(pwr_in_mid)

    # R15 (0805 0R Jumper for +3V3_IN bridging over SDA at X=2.400):
    r15 = load_fp("Resistor_SMD.pretty", "R_0805_2012Metric", "R15")
    r15.SetValue("0R")
    r15.SetPosition(pcbnew.VECTOR2I(mm(2.400), mm(58.000)))
    r15.Reference().SetVisible(False)
    for g in r15.GraphicalItems():
        if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
            g.SetLayer(pcbnew.Dwgs_User)
    board.Add(r15)
    r15.Flip(r15.GetPosition(), False)
    for p in r15.Pads():
        if p.GetPosition().x / 1e6 > 2.400:
            p.SetNet(pwr_in_mid)
        else:
            p.SetNet(pwr_in)

    # Planar B.Cu 0805 0R Jumpers R22..R25 for RGB ring (zero vias, zero F.Cu traces)
    def add_0r_jumper(ref, x, y, vert, net_a, net_b):
        rj = load_fp("Resistor_SMD.pretty", "R_0805_2012Metric", ref)
        rj.SetValue("0R")
        rj.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        rj.Reference().SetVisible(False)
        for g in rj.GraphicalItems():
            if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen', 'F.SilkS', 'B.SilkS'):
                g.SetLayer(pcbnew.Dwgs_User)
        board.Add(rj)
        rj.Flip(rj.GetPosition(), False)
        rj.SetOrientation(pcbnew.EDA_ANGLE(90 if vert else 0, pcbnew.DEGREES_T))
        for p in rj.Pads():
            coord = p.GetPosition().y / 1e6 if vert else p.GetPosition().x / 1e6
            ref_coord = y if vert else x
            p.SetNet(net_a if coord < ref_coord else net_b)

    add_0r_jumper("R22", 17.425, 94.650,  False, rgb_g_west, rgb_nets['G'])  # RGB_G over +3V3 at X=17.425
    add_0r_jumper("R23", 17.425, 96.700,  False, rgb_b_west, rgb_b_north)    # RGB_B_NORTH over +3V3 at X=17.425
    add_0r_jumper("R24", 23.600, 104.900, True,  rgb_r_south, rgb_nets['R']) # RGB_R over +3V3 at Y=104.900
    add_0r_jumper("R25", 31.620, 96.700,  False, rgb_b_north, rgb_nets['B']) # RGB_B over RGB_G vertical drop at X=31.620

    print("=== STEP 3: ROUTE PLANAR TRACKS ON B.CU (ZERO VIAS, ZERO F.CU TRACES) ===")
    def track(x1, y1, x2, y2, net, width=0.20, layer=pcbnew.B_Cu):
        if abs(x1-x2) < 1e-4 and abs(y1-y2) < 1e-4:
            return None
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
        t.SetWidth(mm(width))
        t.SetLayer(layer)
        t.SetNet(net)
        board.Add(t)
        return t

    # 1. Direct Resistor R1..R10 Pad 1 (24.690) to LED D1..D10 Pad 1 (20.675):
    for i in range(10):
        wy = 20.000 + 8.000 * i
        track(24.690, wy, 20.675, wy, led_mid_nets[i])

    # 2. LED Tracks from U1 (30.500, 16.000) to R1..R10 (Pad 2 at 25.710):
    # 2a. D1..D8 (Port 0: pins 11..4) straight down to R1..R8:
    u1_led_x = [27.575, 28.225, 28.875, 29.525, 30.175, 30.825, 31.475, 32.125]
    for i in range(8):
        ux = u1_led_x[i]
        wy = 20.000 + 8.000 * i
        net = led_nets[i]
        track(ux, 18.863, ux, wy, net)
        track(ux, wy, 25.710, wy, net)

    # 2b-d. Port 1 Pins 13..17 (LED_9, LED_10, RGB_R, RGB_G, RGB_B) drop straight South into U1
    #       central channel (Y = 14.50..16.50) and exit East cleanly on B.Cu with zero crossings:
    # LED_9 (Pin 13 at 26.925, 13.137) -> Y=16.50 -> X=34.650 -> R9 Pad 2 (25.710, 84.000):
    track(26.925, 13.137, 26.925, 16.500, led_nets[8])
    track(26.925, 16.500, 34.650, 16.500, led_nets[8])
    track(34.650, 16.500, 34.650, 84.000, led_nets[8])
    track(34.650, 84.000, 25.710, 84.000, led_nets[8])

    # LED_10 (Pin 14 at 27.575, 13.137) -> Y=16.00 -> X=35.150 -> R10 Pad 2 (25.710, 92.000):
    track(27.575, 13.137, 27.575, 16.000, led_nets[9])
    track(27.575, 16.000, 35.150, 16.000, led_nets[9])
    track(35.150, 16.000, 35.150, 92.000, led_nets[9])
    track(35.150, 92.000, 25.710, 92.000, led_nets[9])

    # RGB_G (Pin 15 at 28.225, 13.137) -> Y=15.50 -> X=35.650 -> Y=94.650 -> R17 Pad 1 (31.620, 104.350) & R22 -> X=5.000 -> R20 Pad 1 (6.480, 114.350):
    track(28.225, 13.137, 28.225, 15.500, rgb_nets['G'])
    track(28.225, 15.500, 35.650, 15.500, rgb_nets['G'])
    track(35.650, 15.500, 35.650, 94.650, rgb_nets['G'])
    track(35.650, 94.650, 18.338, 94.650, rgb_nets['G'])  # Outer North bus -> R22 right pad
    track(31.620, 94.650, 31.620, 104.350, rgb_nets['G']) # Vertical drop under R25 at X=31.620 -> R17 Pad 1
    track(16.512, 94.650, 5.000, 94.650, rgb_g_west)       # R22 left pad -> outer West bus
    track(5.000, 94.650, 5.000, 114.350, rgb_g_west)
    track(5.000, 114.350, 6.480, 114.350, rgb_g_west)      # R20 Pad 1

    # RGB_B (Pin 16 at 28.875, 13.137) -> Y=15.00 -> X=36.150 -> R18 Pad 1 (31.620, 114.350) -> R25 (31.620, 96.700) -> R23 -> X=5.800 -> R21 Pad 1 (6.480, 104.350):
    track(28.875, 13.137, 28.875, 15.000, rgb_nets['B'])
    track(28.875, 15.000, 36.150, 15.000, rgb_nets['B'])
    track(36.150, 15.000, 36.150, 114.350, rgb_nets['B'])
    track(36.150, 114.350, 31.620, 114.350, rgb_nets['B']) # R18 Pad 1
    track(34.000, 114.350, 34.000, 96.700, rgb_nets['B'])  # North to Y=96.700
    track(34.000, 96.700, 32.532, 96.700, rgb_nets['B'])   # R25 right pad
    track(30.708, 96.700, 18.338, 96.700, rgb_b_north)     # R25 left pad -> R23 right pad (nested under RGB_G)
    track(16.512, 96.700, 5.800, 96.700, rgb_b_west)       # R23 left pad -> inner West bus
    track(5.800, 96.700, 5.800, 104.350, rgb_b_west)
    track(5.800, 104.350, 6.480, 104.350, rgb_b_west)      # R21 Pad 1

    # RGB_R (Pin 17 at 29.525, 13.137) -> Y=14.50 -> X=36.650 -> R19 Pad 1 (22.960, 119.350) -> R24 -> R16 Pad 1 (22.960, 99.350):
    track(29.525, 13.137, 29.525, 14.500, rgb_nets['R'])
    track(29.525, 14.500, 36.650, 14.500, rgb_nets['R'])
    track(36.650, 14.500, 36.650, 119.350, rgb_nets['R'])
    track(36.650, 119.350, 22.960, 119.350, rgb_nets['R']) # R19 Pad 1
    track(23.600, 119.350, 23.600, 105.812, rgb_nets['R']) # Up to R24 bottom pad
    track(23.600, 103.988, 23.600, 99.350, rgb_r_south)    # R24 top pad -> North
    track(23.600, 99.350, 22.960, 99.350, rgb_r_south)     # R16 Pad 1

    # 2e. D1..D16 direct Cathode (Pad 1) to R16..R21 (Pad 2) + +3V3 Anode ring (Pad 2):
    for idx, (d_num, r_num, ch, dx, dy, rot180) in enumerate(rgb_ring_specs):
        if rot180:
            track(dx - 1.625, dy, dx - 2.890, dy, rgb_mid_nets[idx])
        else:
            track(dx + 1.625, dy, dx + 2.890, dy, rgb_mid_nets[idx])

    # D14 Pad 2 (17.425, 119.350) -> D15/D16 Pad 2 (12.015) -> D11 Pad 2 (17.425, 99.350) -> D12/D13 Pad 2 (26.085) -> up X=17.425 to D10..D1:
    track(17.425, 119.350, 15.100, 119.350, pwr)
    track(15.100, 119.350, 15.100, 99.350, pwr)
    track(15.100, 114.350, 12.015, 114.350, pwr) # D15 Pad 2
    track(15.100, 104.350, 12.015, 104.350, pwr) # D16 Pad 2
    track(15.100, 99.350, 17.425, 99.350, pwr)   # D11 Pad 2
    track(15.100, 104.900, 25.000, 104.900, pwr) # Upper chord above M7 hole, under R24
    track(25.000, 104.900, 25.000, 104.350, pwr)
    track(25.000, 104.350, 26.085, 104.350, pwr) # D12 Pad 2
    track(25.000, 104.900, 25.000, 114.350, pwr)
    track(25.000, 114.350, 26.085, 114.350, pwr) # D13 Pad 2

    # +3V3 up X=17.425 (under R23 at 96.700 and R22 at 94.650) across D10..D1 Pad 2:
    track(17.425, 99.350, 17.425, 20.000, pwr)

    # 3. Concentric Non-Crossing Control & Power Routing (all planar on B.Cu):
    r13_p1 = [p for p in r13.Pads() if p.GetPosition().x/1e6 > 4.500][0]
    r13_p2 = [p for p in r13.Pads() if p.GetPosition().x/1e6 < 4.500][0]
    track(8.760, 66.110, r13_p1.GetPosition().x/1e6, 66.110, sda_in)
    track(r13_p2.GetPosition().x/1e6, 66.110, 2.400, 66.110, sda)
    track(2.400, 66.110, 2.400, 6.400, sda)
    track(2.400, 6.400, 33.425, 6.400, sda)
    track(33.425, 6.400, 33.425, 13.137, sda) # U1 Pin 23
    r11_p2 = [p for p in r11.Pads() if str(p.GetNumber()) == '2'][0]
    track(33.425, 8.800, r11_p2.GetPosition().x/1e6, 8.800, sda)

    track(8.760, 68.650, 4.500, 68.650, scl)
    track(4.500, 68.650, 4.500, 7.400, scl)
    track(4.500, 7.400, 32.775, 7.400, scl)
    track(32.775, 7.400, 32.775, 13.137, scl) # U1 Pin 22
    r12_p1 = [p for p in r12.Pads() if p.GetPosition().x/1e6 < 33.425][0]
    track(32.775, 10.600, r12_p1.GetPosition().x/1e6, 10.600, scl)

    r14_p1 = [p for p in r14.Pads() if p.GetPosition().x/1e6 > 4.500][0]
    r14_p2 = [p for p in r14.Pads() if p.GetPosition().x/1e6 < 4.500][0]
    track(13.800, 63.570, 13.800, 62.400, pwr_in_jump)
    track(13.800, 62.400, r14_p1.GetPosition().x/1e6, 62.400, pwr_in_jump)

    r15_p1 = [p for p in r15.Pads() if p.GetPosition().x/1e6 > 2.400][0]
    r15_p2 = [p for p in r15.Pads() if p.GetPosition().x/1e6 < 2.400][0]
    track(r14_p2.GetPosition().x/1e6, 62.400, 3.312, 62.400, pwr_in_mid)
    track(3.312, 62.400, 3.312, 58.000, pwr_in_mid)
    track(3.312, 58.000, r15_p1.GetPosition().x/1e6, 58.000, pwr_in_mid)

    track(r15_p2.GetPosition().x/1e6, 58.000, 1.050, 58.000, pwr_in)
    track(1.050, 58.000, 1.050, 1.100, pwr_in)
    fb1_p1 = [p for p in fb1.Pads() if str(p.GetNumber()) == '1'][0]
    fb1_p2 = [p for p in fb1.Pads() if str(p.GetNumber()) == '2'][0]
    track(1.050, 1.100, 36.800, 1.100, pwr_in)
    track(36.800, 1.100, 36.800, fb1_p1.GetPosition().y/1e6, pwr_in)

    # +3V3 (pwr): FB1 Pad 2 -> C1/C2 Pad 1 (36.320) -> X=35.100 (R11, R12, U1 Pin 24) AND East feeder X=37.350 -> Y=122.500 -> D14 Pad 2 (17.425, 119.350):
    track(36.800, fb1_p2.GetPosition().y/1e6, 36.320, fb1_p2.GetPosition().y/1e6, pwr)
    c1_p1 = [p for p in c1.Pads() if str(p.GetNumber()) == '1'][0]
    c2_p1 = [p for p in c2.Pads() if str(p.GetNumber()) == '1'][0]
    track(36.320, fb1_p2.GetPosition().y/1e6, 36.320, 6.400, pwr)
    track(36.320, 4.200, c1_p1.GetPosition().x/1e6, 4.200, pwr)
    track(36.320, 5.400, c2_p1.GetPosition().x/1e6, 5.400, pwr)
    track(36.320, 6.400, 35.100, 6.400, pwr)
    track(35.100, 6.400, 35.100, 12.500, pwr)
    r11_p1 = [p for p in r11.Pads() if str(p.GetNumber()) == '1'][0]
    track(35.100, 8.800, r11_p1.GetPosition().x/1e6, 8.800, pwr)
    r12_p2 = [p for p in r12.Pads() if p.GetPosition().x/1e6 > 33.425][0]
    track(35.100, 10.600, r12_p2.GetPosition().x/1e6, 10.600, pwr)
    track(35.100, 12.500, 34.075, 12.500, pwr)
    track(34.075, 12.500, 34.075, 13.137, pwr) # U1 Pin 24

    track(36.320, 6.400, 37.350, 6.400, pwr)
    track(37.350, 6.400, 37.350, 122.500, pwr)
    track(37.350, 122.500, 17.425, 122.500, pwr)
    track(17.425, 122.500, 17.425, 119.350, pwr) # D14 Pad 2 (0 crossings)

    # Ground Connections (planar on B.Cu):
    # 1. South row pins 1..3 (32.775..34.075) straight South into zone_b GND pour:
    track(32.775, 18.863, 34.075, 18.863, gnd)
    track(34.075, 18.863, 34.075, 22.000, gnd)
    # 2. Pin 12 (VSS at 26.925, 18.863) West into zone_b GND pour:
    track(26.925, 18.863, 24.000, 18.863, gnd)
    # 3. North row unused pins 18..21 (30.175..32.125) up at Pin 18 (30.175) -> Y=9.000 -> X=6.500 -> Y=20.000 into zone_b GND pour:
    track(30.175, 13.137, 32.125, 13.137, gnd)
    track(30.175, 13.137, 30.175, 9.000, gnd)
    track(30.175, 9.000, 6.500, 9.000, gnd)
    track(6.500, 9.000, 6.500, 20.000, gnd)
    # 4. C1/C2 GND (37.280 -> 37.650) North-West perimeter Y=0.550 -> X=0.550 -> Y=71.500 -> X=8.760 into zone_b & J1 GND:
    c1_p2 = [p for p in c1.Pads() if str(p.GetNumber()) == '2'][0]
    c2_p2 = [p for p in c2.Pads() if str(p.GetNumber()) == '2'][0]
    track(c1_p2.GetPosition().x/1e6, 4.200, 37.650, 4.200, gnd)
    track(c2_p2.GetPosition().x/1e6, 5.400, 37.650, 5.400, gnd)
    track(37.650, 5.400, 37.650, 0.550, gnd)
    track(37.650, 0.550, 0.550, 0.550, gnd)
    track(0.550, 0.550, 0.550, 71.500, gnd)
    track(0.550, 71.500, 8.760, 71.500, gnd)
    track(0.550, 71.500, 0.550, 125.000, gnd)
    track(0.550, 125.000, 8.000, 125.000, gnd)

    # Ensure all dial scale graphics are on F.Silkscreen, NOT F.Cu or F.Mask:
    for fp in board.Footprints():
        for g in fp.GraphicalItems():
            if g.GetLayerName() in ('F.Cu', 'F.Mask'):
                g.SetLayer(pcbnew.F_SilkS)

    # Add prominent B.SilkS Pin 1 / Cathode markers for JLCPCB SMT polarity confirmation
    def add_bsilk_dot(cx, cy, radius=0.45):
        dot = pcbnew.PCB_SHAPE(board)
        dot.SetShape(pcbnew.SHAPE_T_CIRCLE)
        dot.SetFilled(True)
        dot.SetCenter(pcbnew.VECTOR2I(mm(cx), mm(cy)))
        dot.SetRadius(mm(radius))
        dot.SetLayer(pcbnew.B_SilkS)
        dot.SetWidth(mm(0.10))
        board.Add(dot)

    def add_bsilk_text(label, tx, ty):
        txt = pcbnew.PCB_TEXT(board)
        txt.SetText(label)
        txt.SetPosition(pcbnew.VECTOR2I(mm(tx), mm(ty)))
        txt.SetTextSize(pcbnew.VECTOR2I(mm(1.0), mm(1.0)))
        txt.SetTextThickness(mm(0.18))
        txt.SetLayer(pcbnew.B_SilkS)
        txt.SetMirrored(True)
        txt.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        txt.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
        board.Add(txt)

    # U1 (PCA9555PW Pin 1 at 34.075, 18.863) & J1 (Pin 1 at 8.760, 63.570)
    add_bsilk_dot(35.00, 18.863, 0.35)
    add_bsilk_text("1", 35.00, 20.20)
    add_bsilk_dot(11.20, 63.57, 0.45)
    add_bsilk_text("1", 11.20, 62.00)
    # D1..D10 & D11..D16 Cathode (Pin 1) markers
    for i in range(10):
        add_bsilk_dot(19.050 + 1.625, 20.000 + 8.000 * i - 1.35, 0.25)
    for _, _, _, dx, dy, rot180 in rgb_ring_specs:
        kx = (dx - 1.625) if rot180 else (dx + 1.625)
        add_bsilk_dot(kx, dy - 1.35, 0.25)

    # Bottom blind-milled pockets for 10 VU bar-graph LEDs D1..D10 (User.1 + B.Mask, NO front holes)
    # Clears 1.86 x 1.60 mm lens inside 2.00 x 1.80 mm pocket (0.20 mm clear of copper pads at ±2.05 / ±1.20 mm)
    enabled_layers = board.GetEnabledLayers()
    enabled_layers.AddLayer(pcbnew.User_1)
    board.SetEnabledLayers(enabled_layers)
    for i in range(10):
        wy = 20.000 + 8.000 * i
        bm = pcbnew.PCB_SHAPE(board)
        bm.SetShape(pcbnew.SHAPE_T_RECT)
        bm.SetFilled(True)
        bm.SetStart(pcbnew.VECTOR2I(mm(18.050), mm(wy - 0.900)))
        bm.SetEnd(pcbnew.VECTOR2I(mm(20.050), mm(wy + 0.900)))
        bm.SetLayer(pcbnew.B_Mask)
        bm.SetWidth(0)
        board.Add(bm)

        bs = pcbnew.PCB_SHAPE(board)
        bs.SetShape(pcbnew.SHAPE_T_RECT)
        bs.SetFilled(False)
        bs.SetStart(pcbnew.VECTOR2I(mm(18.050), mm(wy - 0.900)))
        bs.SetEnd(pcbnew.VECTOR2I(mm(20.050), mm(wy + 0.900)))
        bs.SetLayer(pcbnew.User_1)
        bs.SetWidth(mm(0.10))
        board.Add(bs)

    def add_user_text(layer, text, x, y, size=0.80, thickness=0.12, halign=pcbnew.GR_TEXT_H_ALIGN_LEFT, angle_deg=0.0):
        t = pcbnew.PCB_TEXT(board)
        t.SetText(text)
        t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
        t.SetTextThickness(mm(thickness))
        t.SetLayer(layer)
        t.SetHorizJustify(halign)
        if angle_deg:
            t.SetTextAngle(pcbnew.EDA_ANGLE(angle_deg, pcbnew.DEGREES_T))
        board.Add(t)

    def add_user_line(layer, x1, y1, x2, y2, width=0.12):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        seg.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
        seg.SetLayer(layer)
        seg.SetWidth(mm(width))
        board.Add(seg)

    def add_user_rect(layer, x1, y1, x2, y2, width=0.15):
        rect = pcbnew.PCB_SHAPE(board)
        rect.SetShape(pcbnew.SHAPE_T_RECT)
        rect.SetFilled(False)
        rect.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        rect.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
        rect.SetLayer(layer)
        rect.SetWidth(mm(width))
        board.Add(rect)

    # User.1 CNC Blind-Slot Callouts (strictly outside X=0..38.10mm so interior stays pure 10x toolpath rects)
    u1_header = [
        ("BLIND SLOT CNC MILLING LAYER (User.1)", 1.05, 0.16),
        ("10x RECTANGULAR BLIND POCKETS (D1..D10): 2.00mm (X) x 1.80mm (Y) @ X=19.050mm, Y=20.000..92.000mm (8.000mm PITCH)", 0.80, 0.12),
        ("ENTER FROM B.Cu (BOTTOM) SIDE ONLY. MILL DEPTH = 1.30mm +/- 0.15mm INTO 2.00mm FR4 BOARD.", 0.80, 0.12),
        ("REMAINING FR4 THICKNESS ON F.Cu (TOP/FRONT) = 0.70mm SOLID TRANSLUCENT WEB. DO NOT CUT THROUGH F.Cu!", 0.80, 0.12),
        ("B.Cu SMT PADS ARE AT X=17.425 / 20.675mm (INNER COPPER EDGES AT X=17.850 / 20.250mm -> 0.200mm CLEARANCE TO POCKET).", 0.80, 0.12),
    ]
    uy = 4.0
    for txt, sz, th in u1_header:
        add_user_text(pcbnew.User_1, txt, 42.0, uy, size=sz, thickness=th)
        uy += 2.6
    for i in range(10):
        wy = 20.000 + 8.000 * i
        add_user_text(
            pcbnew.User_1,
            f"<- D{i+1} BOTTOM BLIND SLOT: 2.00x1.80mm @ (19.05, {wy:.2f}) | MILL FROM B.Cu DEPTH=1.30mm (LEAVE 0.70mm FR4 ON F.Cu)",
            42.0, wy, size=0.80, thickness=0.12,
        )

    # Cmts.User Board Dimension Callouts & Feature Leaders
    add_user_line(pcbnew.Cmts_User, 0.0, -4.0, 38.10, -4.0)
    add_user_line(pcbnew.Cmts_User, 0.0, -5.0, 0.0, -1.0)
    add_user_line(pcbnew.Cmts_User, 38.10, -5.0, 38.10, -1.0)
    add_user_text(pcbnew.Cmts_User, '38.10 mm (1.500") VPR-500 WIDTH', 19.05, -5.8, size=0.85, thickness=0.13, halign=pcbnew.GR_TEXT_H_ALIGN_CENTER)

    add_user_line(pcbnew.Cmts_User, -4.0, 0.0, -4.0, 133.35)
    add_user_line(pcbnew.Cmts_User, -5.0, 0.0, -1.0, 0.0)
    add_user_line(pcbnew.Cmts_User, -5.0, 133.35, -1.0, 133.35)
    add_user_text(pcbnew.Cmts_User, '133.35 mm (5.250") VPR-500 HEIGHT', -5.8, 33.0, size=0.85, thickness=0.13, halign=pcbnew.GR_TEXT_H_ALIGN_CENTER, angle_deg=90.0)

    cmts_leaders = [
        (19.05, 3.96,    -9.0, 3.96,    'MH1: Ø3.20mm NPTH VPR-500 RACK MOUNT HOLE (Y=3.96mm, 125.43mm / 4.938" SPAN TO MH2)'),
        (10.31, 14.525,  -9.0, 14.525,  'BR1: WUERTH 7466303 (C5523891) SMT M3 RIGHT-ANGLE BRACKET ON B.Cu (104.300mm SPAN)'),
        (19.05, 52.00,   -9.0, 52.00,   'D1..D10: 10x VU BAR-GRAPH LEDs ON B.Cu -> BLIND-MILL 2.00x1.80mm POCKETS 1.30mm DEEP FROM B.Cu (0.70mm FR4, NO FRONT HOLES)'),
        (11.28, 75.00,   -9.0, 75.00,   'J1: 2x10 SMD VERTICAL SOCKET ON B.Cu (MATES TO CARRIER U6 RIGHT-ANGLE HEADER)'),
        (10.39, 104.35,  -9.0, 99.50,   'D11..D16: 6x SKIRT RGB RING LEDs ON B.Cu (R=10.00mm) -> 1.92x1.68mm NPTH THROUGH-SLOTS UNDER KNOB SKIRT'),
        (19.05, 109.35,  -9.0, 109.35,  'ENC (Edge.Cuts): Ø7.20mm PEC11R M7 BUSHING CUTOUT @ (19.05, 109.35) + Ø2.20mm ANTI-ROT PIN @ (11.55, 109.35)'),
        (10.31, 118.825, -9.0, 118.825, 'BR2: WUERTH 7466303 (C5523891) SMT M3 RIGHT-ANGLE BRACKET ON B.Cu (Y=118.825mm)'),
        (19.05, 129.39,  -9.0, 129.39,  'MH2: Ø3.20mm NPTH VPR-500 RACK MOUNT HOLE (Y=129.39mm)'),
    ]
    for tx, ty, lx, ly, label in cmts_leaders:
        add_user_line(pcbnew.Cmts_User, tx, ty, lx + 0.8, ly)
        add_user_text(pcbnew.Cmts_User, label, lx, ly, size=0.80, thickness=0.12, halign=pcbnew.GR_TEXT_H_ALIGN_RIGHT)

    # Cmts.User Bordered CAM & PCBA Manufacturing Notes Block (Right of Board)
    add_user_rect(pcbnew.Cmts_User, 42.0, 4.0, 156.0, 128.0, width=0.18)
    cam_notes = [
        ("CAM & PCBA MANUFACTURING NOTES - ICIO500 ACTIVE FACEPLATE (VPR-500)", 1.05, 0.16),
        ("", 0.60, 0.10),
        ("1. BOARD FABRICATION SPECIFICATIONS:", 0.90, 0.14),
        ("   - SIZE: 38.10 x 133.35 mm (1.500\" x 5.250\"), 2-LAYER FR4 (F.Cu, B.Cu), THICKNESS = 2.00 mm (+/-10%)", 0.80, 0.12),
        ("   - SOLDERMASK: MATTE BLACK BOTH SIDES | SILKSCREEN: WHITE | FINISH: ENIG OR LEAD-FREE HASL", 0.80, 0.12),
        ("   - ROUTING: 100% SINGLE-SIDED B.Cu PLANAR TRACES (0 VIAS, 0.0mm F.Cu SIGNAL TRACES)", 0.80, 0.12),
        ("", 0.60, 0.10),
        ("2. BOTTOM BLIND-MILLED SLOTS D1..D10 (NO FRONT HOLES):", 0.90, 0.14),
        ("   - FILE: faceplate_front-Bottom_Blind_Slots_Depth_1.3mm.gbr (KiCad User.1) | JLCPCB: ENABLE BLIND SLOT = YES", 0.80, 0.12),
        ("   - GEOMETRY: 10x POCKETS 2.00mm (X) x 1.80mm (Y) CENTERED AT X=19.05mm, Y=20.00..92.00mm (8.00mm PITCH)", 0.80, 0.12),
        ("   - DEPTH: MILL 1.30mm +/- 0.15mm DEEP FROM B.Cu (BOTTOM) SIDE ONLY -> LEAVES 0.70mm SOLID FR4 SKIN ON F.Cu", 0.80, 0.12),
        ("   - CLEARANCE: NO FRONT THROUGH-HOLES ON D1..D10; B.Mask ALSO OPENED 2.00x1.80mm; 0.20mm CLEAR TO PADS", 0.80, 0.12),
        ("", 0.60, 0.10),
        ("3. THROUGH-SLOTS & MECHANICAL NPTH DRILLS (faceplate_front.drl):", 0.90, 0.14),
        ("   - SKIRT LEDS D11..D16: 6x 1.92 x 1.68 mm FULL NPTH OVAL THROUGH-SLOTS CUT ALL THE WAY THROUGH 2.0mm FR4", 0.80, 0.12),
        ("   - HIDDEN UNDER 12.7mm CAPSTAN KNOB SKIRT (R=10.00mm AROUND (19.05, 109.35), 0.265mm CLEAR TO PADS)", 0.80, 0.12),
        ("   - RACK HOLES MH1/MH2: 2x Ø3.20mm NPTH @ (19.05, 3.96) & (19.05, 129.39) | ENC CUTOUTS ON Edge.Cuts: Ø7.20mm @ (19.05, 109.35) + Ø2.20mm @ (11.55, 109.35)", 0.80, 0.12),
        ("", 0.60, 0.10),
        ("4. PCBA / BOTTOM SMT ASSEMBLY NOTES (B.Cu ONLY):", 0.90, 0.14),
        ("   - SINGLE-SIDED BOTTOM SMT ONLY (48 COMPONENTS ON B.Cu IN faceplate_cpl.csv, 0 PARTS ON F.Cu)", 0.80, 0.12),
        ("   - D1..D16 (XL-3216...-FB REVERSE-MOUNT): 1.86x1.60x0.52mm CLEAR LENS PROTRUDES DOWN INTO POCKET / SLOT", 0.80, 0.12),
        ("   - LED POLARITY: PIN 1 (CATHODE -) MARKED BY B.SilkS DOT; D1..D14 ROT=180 deg, D15..D16 ROT=0 deg", 0.80, 0.12),
        ("   - U1 PCA9555PW P1_2=RGB_G, P1_3=RGB_B, P1_4=RGB_R | 0805 0R PLANAR JUMPERS: R13..R15, R22..R25 (C17414)", 0.80, 0.12),
        ("   - BR1/BR2 WUERTH WP-SMRA-M3 (7466303 / C5523891) ON B.Cu; J1 2x10 HEADER MATES CARRIER U6", 0.80, 0.12),
    ]
    cy = 8.0
    for txt, sz, th in cam_notes:
        if txt:
            add_user_text(pcbnew.Cmts_User, txt, 44.0, cy, size=sz, thickness=th)
            cy += 3.2
        else:
            cy += 1.6

    # Add F.Mask optical porthole windows (Ø3.6 mm) over D11..D16 so light shines through translucent FR4
    for _, _, _, dx, dy, _ in rgb_ring_specs:
        win = pcbnew.PCB_SHAPE(board)
        win.SetShape(pcbnew.SHAPE_T_CIRCLE)
        win.SetFilled(True)
        win.SetCenter(pcbnew.VECTOR2I(mm(dx), mm(dy)))
        win.SetRadius(mm(1.80))
        win.SetLayer(pcbnew.F_Mask)
        win.SetWidth(mm(0.05))
        board.Add(win)

    # Step 4: Copper Zones
    W, H = 38.10, 133.35

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
    # Cutout around encoder dial bushing and anti-rotation hole:
    out_f.NewHole()
    out_f.Append(mm(8.5), mm(104.5))
    out_f.Append(mm(24.0), mm(104.5))
    out_f.Append(mm(24.0), mm(114.5))
    out_f.Append(mm(8.5), mm(114.5))
    for _, _, _, dx, dy, _ in rgb_ring_specs:
        out_f.NewHole()
        out_f.Append(mm(dx - 2.0), mm(dy - 2.0))
        out_f.Append(mm(dx + 2.0), mm(dy - 2.0))
        out_f.Append(mm(dx + 2.0), mm(dy + 2.0))
        out_f.Append(mm(dx - 2.0), mm(dy + 2.0))
    zone_f.SetMinThickness(mm(0.20))
    zone_f.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    board.Add(zone_f)

    zone_b = pcbnew.ZONE(board)
    lset_b = pcbnew.LSET()
    lset_b.AddLayer(pcbnew.B_Cu)
    zone_b.SetLayerSet(lset_b)
    zone_b.SetLayer(pcbnew.B_Cu)
    zone_b.SetNet(gnd)
    out_b = zone_b.Outline()
    out_b.NewOutline()
    out_b.Append(mm(6.2), mm(13.0))
    out_b.Append(mm(W-0.5), mm(13.0))
    out_b.Append(mm(W-0.5), mm(H-0.5))
    out_b.Append(mm(6.2), mm(H-0.5))
    for i in range(10):
        wy = 20.000 + 8.000 * i
        wx1, wx2 = 13.05, 25.05
        wy1, wy2 = wy - 2.0, wy + 2.0
        out_b.NewHole()
        out_b.Append(mm(wx1), mm(wy1))
        out_b.Append(mm(wx2), mm(wy1))
        out_b.Append(mm(wx2), mm(wy2))
        out_b.Append(mm(wx1), mm(wy2))
    # Cutout around encoder dial bushing and anti-rotation hole:
    out_b.NewHole()
    out_b.Append(mm(8.5), mm(104.5))
    out_b.Append(mm(24.0), mm(104.5))
    out_b.Append(mm(24.0), mm(114.5))
    out_b.Append(mm(8.5), mm(114.5))
    for _, _, _, dx, dy, _ in rgb_ring_specs:
        out_b.NewHole()
        out_b.Append(mm(dx - 2.0), mm(dy - 2.0))
        out_b.Append(mm(dx + 2.0), mm(dy - 2.0))
        out_b.Append(mm(dx + 2.0), mm(dy + 2.0))
        out_b.Append(mm(dx - 2.0), mm(dy + 2.0))
    zone_b.SetMinThickness(mm(0.20))
    zone_b.SetThermalReliefGap(mm(0.25))
    zone_b.SetThermalReliefSpokeWidth(mm(0.25))
    zone_b.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    board.Add(zone_b)

    board.BuildConnectivity()
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
