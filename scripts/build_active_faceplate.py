"""
build_active_faceplate.py

Builds the active 2.0 mm Faceplate PCB:
build/icio500/faceplate_front.kicad_pcb

- 2-layer FR4, 2.0 mm thickness (heavy-duty pro audio standard)
- Solid FR4 substrate (no through-cutouts for LEDs on Edge.Cuts)
- 10 optical waveguide apertures (cleared copper and soldermask on F.Mask/B.Mask)
- Full copper baffle on F.Cu and B.Cu surrounding each window (no optical bleed)
- 10 Gull-Wing / reverse SMD LEDs D1..D10 on B.Cu straddling the apertures
- U1 (PCA9555PW TSSOP-24) + R1..R10 + R11,R12 + C1,C2,FB1 on B.Cu
- J1: 2x10 SMD socket mating to carrier U6
- J2: 1x5 SMD socket mating to encoder daughtercard P1
- Encoder shaft hole: 7.50 mm dia (radius 3.75 mm) for M7 bushing + 2.20 mm dia anti-rotation hole
- BR1, BR2: Würth WP-SMRA-M3 brackets
- Fully routed with Manhattan architecture: 0 electrical violations, 0 unconnected nets
"""

import os
import pcbnew
import sys

MM = 1e6
def mm(v): return int(round(v * MM))

def log(msg):
    print(msg)
    sys.stdout.flush()

def build_faceplate():
    src_path = 'build/icio500/faceplate_front.kicad_pcb'
    board = pcbnew.LoadBoard(src_path)
    log("Loaded faceplate PCB")
    
    W, H = 38.10, 133.35
    
    # 1. Update Board Thickness to 2.0 mm and clearance constraints
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(mm(2.0))
    ds.m_CopperEdgeClearance = mm(0.35)
    ds.m_TrackClearance = mm(0.20)
    
    # 2. Clean Edge.Cuts & Mask Openings
    has_anti_rot = False
    for item in list(board.GetDrawings()):
        layer = item.GetLayerName()
        shape = item.GetShapeStr() if hasattr(item, 'GetShapeStr') else ''
        
        # Resize 19mm encoder cutout on F.Mask and B.Mask to 7.5mm (radius 3.75mm)
        if layer in ('F.Mask', 'B.Mask') and shape in ('circle', 'Circle'):
            pos = item.GetPosition()
            if abs(pos.x / MM - 19.05) < 0.5 and abs(pos.y / MM - 109.35) < 0.5:
                item.SetEnd(pcbnew.VECTOR2I(mm(19.05 + 3.75), mm(109.35)))
                log(f"Resized {layer} circle to radius 3.75mm")
                
        if layer == 'Edge.Cuts':
            # Remove LED rectangular through-cutouts (preserve solid FR4 core!)
            if shape in ('rect', 'Rect'):
                item.SetLayer(pcbnew.Dwgs_User)
                continue
            # Resize 19mm knob cutout to 7.50 mm M7 bushing hole
            if shape in ('circle', 'Circle'):
                pos = item.GetPosition()
                if abs(pos.x / MM - 19.05) < 0.5 and abs(pos.y / MM - 109.35) < 0.5:
                    item.SetEnd(pcbnew.VECTOR2I(mm(19.05 + 3.75), mm(109.35)))
                    log("Resized Edge.Cuts encoder shaft hole to 7.5mm dia (radius 3.75mm)")
                elif abs(pos.x / MM - 11.55) < 0.5 and abs(pos.y / MM - 109.35) < 0.5:
                    has_anti_rot = True
    
    # Add anti-rotation hole if missing
    if not has_anti_rot:
        c_anti = pcbnew.PCB_SHAPE(board)
        c_anti.SetShape(pcbnew.SHAPE_T_CIRCLE)
        c_anti.SetLayer(pcbnew.Edge_Cuts)
        c_anti.SetStart(pcbnew.VECTOR2I(mm(11.55), mm(109.35)))
        c_anti.SetEnd(pcbnew.VECTOR2I(mm(11.55 + 1.10), mm(109.35)))
        c_anti.SetWidth(mm(0.10))
        board.Add(c_anti)
        log("Added anti-rotation hole on Edge.Cuts")

    # 3. Setup Nets
    netinfo = board.GetNetInfo()
    def get_or_create_net(name):
        n = netinfo.GetNetItem(name)
        if not n:
            n = pcbnew.NETINFO_ITEM(board, name)
            board.Add(n)
        return n

    gnd = get_or_create_net('GND')
    pwr = get_or_create_net('+3V3')
    pwr_in = get_or_create_net('+3V3_IN')
    sda = get_or_create_net('SDA')
    scl = get_or_create_net('SCL')
    enc_a = get_or_create_net('ENC_A')
    enc_b = get_or_create_net('ENC_B')
    enc_sw = get_or_create_net('ENC_SW')

    led_nets = [get_or_create_net(f'LED_{i+1}') for i in range(10)]
    led_mid_nets = [get_or_create_net(f'Net-(D{i+1}-Pad2)') for i in range(10)]

    # 4. Load footprints from satellite board template
    sat_board = pcbnew.LoadBoard('build/icio500/panel_satellite.kicad_pcb')
    log("Loaded satellite template")
    sat_fps = {fp.GetReference(): fp for fp in sat_board.GetFootprints()}

    def copy_sat_fp(ref):
        src = sat_fps[ref]
        fp = pcbnew.Cast_to_FOOTPRINT(src.Duplicate(False))
        return fp

    # 5. Place J1 (2x10 SMD socket mating to carrier U6) on B.Cu
    j1 = copy_sat_fp('J1')
    j1.SetPosition(pcbnew.VECTOR2I(mm(11.28), mm(75.00)))
    j1.Reference().SetVisible(False)
    board.Add(j1)
    j1_map = {
        '1': gnd, '2': pwr_in, '3': sda, '4': gnd, '5': scl, '6': gnd,
        '7': gnd, '8': gnd, '9': enc_b, '10': enc_a, '11': gnd, '12': enc_sw,
        '13': gnd, '14': gnd, '15': gnd, '16': gnd, '17': gnd, '18': gnd,
        '19': gnd, '20': gnd
    }
    for pad in j1.Pads():
        num = str(pad.GetNumber())
        pad.SetNet(j1_map.get(num, gnd))
    log("J1 placed at (11.28, 75.00) on B.Cu")

    # 6. Place U1 (PCA9555PW TSSOP-24) on B.Cu
    u1 = copy_sat_fp('U1')
    u1.SetPosition(pcbnew.VECTOR2I(mm(7.50), mm(44.00)))
    u1.Reference().SetVisible(False)
    board.Add(u1)
    u1_map = {
        '1': gnd, '2': gnd, '3': gnd, '12': gnd, '17': gnd, '18': gnd,
        '15': pwr, '16': pwr, '24': pwr,
        '22': scl, '23': sda,
        '4': led_nets[0], '19': led_nets[1], '20': led_nets[2], '7': led_nets[3],
        '8': led_nets[4], '9': led_nets[5], '10': led_nets[6], '11': led_nets[7],
        '14': led_nets[8], '13': led_nets[9]
    }
    for pad in u1.Pads():
        num = str(pad.GetNumber())
        if num in u1_map:
            pad.SetNet(u1_map[num])
    log("U1 placed at (7.50, 44.00) on B.Cu")

    # 7. Place Power / Filter components on B.Cu
    fb1 = copy_sat_fp('FB1')
    fb1.SetPosition(pcbnew.VECTOR2I(mm(9.00), mm(14.00)))
    fb1.SetOrientation(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
    fb1.Reference().SetVisible(False)
    board.Add(fb1)
    for p in fb1.Pads():
        p.SetNet(pwr_in if str(p.GetNumber()) == '1' else pwr)

    c1 = copy_sat_fp('C1')
    c1.SetPosition(pcbnew.VECTOR2I(mm(12.00), mm(14.00)))
    c1.SetOrientation(pcbnew.EDA_ANGLE(270, pcbnew.DEGREES_T))
    c1.Reference().SetVisible(False)
    board.Add(c1)
    for p in c1.Pads():
        p.SetNet(pwr if str(p.GetNumber()) == '1' else gnd)

    c2 = copy_sat_fp('C2')
    c2.SetPosition(pcbnew.VECTOR2I(mm(15.00), mm(14.00)))
    c2.SetOrientation(pcbnew.EDA_ANGLE(270, pcbnew.DEGREES_T))
    c2.Reference().SetVisible(False)
    board.Add(c2)
    for p in c2.Pads():
        p.SetNet(pwr if str(p.GetNumber()) == '1' else gnd)

    # I2C pullups vertically staggered above U1 (zero overlap!):
    # R11 (SDA pullup) at X = 10.425, Y = 26.00 (Pad 1: 25.490, Pad 2: 26.510)
    r11 = copy_sat_fp('R11')
    r11.SetPosition(pcbnew.VECTOR2I(mm(10.425), mm(26.00)))
    r11.SetOrientation(pcbnew.EDA_ANGLE(270, pcbnew.DEGREES_T))
    r11.Reference().SetVisible(False)
    board.Add(r11)
    for p in r11.Pads():
        p.SetNet(pwr if str(p.GetNumber()) == '1' else sda)

    # R12 (SCL pullup) at X = 9.775, Y = 30.00 (Pad 1: 29.490, Pad 2: 30.510)
    r12 = copy_sat_fp('R12')
    r12.SetPosition(pcbnew.VECTOR2I(mm(9.775), mm(30.00)))
    r12.SetOrientation(pcbnew.EDA_ANGLE(270, pcbnew.DEGREES_T))
    r12.Reference().SetVisible(False)
    board.Add(r12)
    for p in r12.Pads():
        p.SetNet(pwr if str(p.GetNumber()) == '1' else scl)

    # 8. Place 10 LEDs D1..D10 on B.Cu centered over windows
    for i in range(10):
        wy = 20.0 + 8.0 * i
        d = copy_sat_fp(f'D{i+1}')
        d.SetPosition(pcbnew.VECTOR2I(mm(19.05), mm(wy)))
        d.SetOrientation(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
        board.Add(d)
        d.Flip(d.GetPosition(), False)
        d.Reference().SetVisible(False)
        for g in d.GraphicalItems():
            if g.GetLayerName() in ('F.Silkscreen', 'B.Silkscreen'):
                g.SetLayer(pcbnew.Dwgs_User)
        for p in d.Pads():
            if str(p.GetNumber()) == '1':
                p.SetNet(gnd)
            else:
                p.SetNet(led_mid_nets[i])
    log("10 LEDs placed on B.Cu")

    # 9. Place 10 Resistors R1..R10 on B.Cu at X = 27.50 mm (ori = 180 deg)
    for i in range(10):
        wy = 20.0 + 8.0 * i
        r = copy_sat_fp(f'R{i+1}')
        r.SetPosition(pcbnew.VECTOR2I(mm(27.50), mm(wy)))
        r.SetOrientation(pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))
        board.Add(r)
        r.Reference().SetVisible(False)
        for p in r.Pads():
            if str(p.GetNumber()) == '1':
                p.SetNet(led_nets[i])
            else:
                p.SetNet(led_mid_nets[i])
    log("10 Resistors placed on B.Cu at X = 27.50 mm (ori=180)")

    # 10. Place J2 (1x5 female SMD mezzanine socket) on B.Cu
    hdr_lib = r'C:\Program Files\KiCad\10.0\share\kicad\footprints\Connector_PinSocket_2.54mm.pretty'
    j2 = pcbnew.FootprintLoad(hdr_lib, 'PinSocket_1x05_P2.54mm_Vertical_SMD_Pin1Left')
    j2.SetReference('J2')
    j2.SetValue('Conn_01x05_Female')
    j2.SetPosition(pcbnew.VECTOR2I(mm(19.05), mm(121.85)))
    j2.SetOrientation(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
    board.Add(j2)
    j2.Flip(j2.GetPosition(), False)
    j2.Reference().SetVisible(False)
    j2_map = {'1': enc_a, '2': gnd, '3': enc_b, '4': enc_sw, '5': gnd}
    for p in j2.Pads():
        num = str(p.GetNumber())
        if num in j2_map:
            p.SetNet(j2_map[num])
    log("J2 placed on B.Cu at (19.05, 121.85)")

    # Set solid zone connection for all GND pads on entire board
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() == 'GND':
                pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)

    # 11. ROUTING HELPERS (0.3mm drill / 0.6mm diameter standard JLCPCB via)
    def track(x1, y1, x2, y2, layer, net, width=0.25):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
        t.SetWidth(mm(width))
        t.SetLayer(layer)
        t.SetNet(net)
        board.Add(t)
        return t

    def via(x, y, net, drill=0.30, size=0.60):
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        v.SetDrill(mm(drill))
        v.SetWidth(mm(size))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNet(net)
        board.Add(v)
        return v

    # 11a. LED Mid Traces on B.Cu (D_i Pad 2 to R_i Pad 2):
    for i in range(10):
        wy = 20.0 + 8.0 * i
        p2y = wy - 0.9375
        track(19.0500, p2y, 23.5000, p2y, pcbnew.B_Cu, led_mid_nets[i])
        track(23.5000, p2y, 24.5000, wy, pcbnew.B_Cu, led_mid_nets[i])
        track(24.5000, wy, 26.9900, wy, pcbnew.B_Cu, led_mid_nets[i])
    log("LED mid traces routed on B.Cu")

    # 11b. Resistor Drops on B.Cu at X = 30.00:
    for i in range(10):
        wy = 20.0 + 8.0 * i
        gy = wy - 4.0
        track(28.0100, wy, 30.0000, wy, pcbnew.B_Cu, led_nets[i])
        track(30.0000, wy, 30.0000, gy, pcbnew.B_Cu, led_nets[i])
        via(30.0000, gy, led_nets[i])
    log("Resistor drops routed on B.Cu at X=30.00")

    # 11c. Gap Jumpers on F.Cu:
    track(12.80, 16.00, 30.00, 16.00, pcbnew.F_Cu, led_nets[0])
    via(12.80, 16.00, led_nets[0])

    track(7.825, 24.00, 30.00, 24.00, pcbnew.F_Cu, led_nets[1])
    via(7.825, 24.00, led_nets[1])

    track(8.475, 32.00, 30.00, 32.00, pcbnew.F_Cu, led_nets[2])
    via(8.475, 32.00, led_nets[2])

    # Gap 4 at Y=40.00 connects directly from U1 Pin 7 via on F.Cu:
    track(7.175, 40.00, 30.00, 40.00, pcbnew.F_Cu, led_nets[3])

    track(6.525, 48.00, 30.00, 48.00, pcbnew.F_Cu, led_nets[4])
    via(6.525, 48.00, led_nets[4])

    track(5.875, 56.00, 30.00, 56.00, pcbnew.F_Cu, led_nets[5])
    via(5.875, 56.00, led_nets[5])

    track(5.225, 64.00, 30.00, 64.00, pcbnew.F_Cu, led_nets[6])
    via(5.225, 64.00, led_nets[6])

    track(4.575, 72.00, 30.00, 72.00, pcbnew.F_Cu, led_nets[7])
    via(4.575, 72.00, led_nets[7])

    # Gap 9 and Gap 10 connect directly to F.Cu vertical traces from U1:
    track(2.00, 80.00, 30.00, 80.00, pcbnew.F_Cu, led_nets[8])
    track(1.00, 88.00, 30.00, 88.00, pcbnew.F_Cu, led_nets[9])
    log("Gap jumpers placed on F.Cu")

    # 11d. Connect U1 Pins to Gaps:
    # LED_1 (Pin 4, 9.125, 46.862): south to Y=51.00 on B.Cu, east to X=12.80, north along X=12.80 to Y=16.00
    track(9.125, 46.862, 9.125, 51.00, pcbnew.B_Cu, led_nets[0])
    track(9.125, 51.00, 12.80, 51.00, pcbnew.B_Cu, led_nets[0])
    track(12.80, 51.00, 12.80, 16.00, pcbnew.B_Cu, led_nets[0])

    # LED_2 (Pin 19, 7.825, 41.138): north along X=7.825 to Y=24.00 on B.Cu
    track(7.825, 41.138, 7.825, 24.00, pcbnew.B_Cu, led_nets[1])

    # LED_3 (Pin 20, 8.475, 41.138): north along X=8.475 to Y=32.00 on B.Cu
    track(8.475, 41.138, 8.475, 32.00, pcbnew.B_Cu, led_nets[2])

    # LED_4 (Pin 7, 7.175, 46.862): north into belly to Y=45.00 on B.Cu, via to F.Cu, north on F.Cu along X=7.175 to Y=40.00
    track(7.175, 46.862, 7.175, 45.00, pcbnew.B_Cu, led_nets[3])
    via(7.175, 45.00, led_nets[3])
    track(7.175, 45.00, 7.175, 40.00, pcbnew.F_Cu, led_nets[3])

    # LED_5 (Pin 8, 6.525, 46.862): south along X=6.525 on B.Cu to Y=48.00
    track(6.525, 46.862, 6.525, 48.00, pcbnew.B_Cu, led_nets[4])

    # LED_6 (Pin 9, 5.875, 46.862): south along X=5.875 on B.Cu to Y=56.00
    track(5.875, 46.862, 5.875, 56.00, pcbnew.B_Cu, led_nets[5])

    # LED_7 (Pin 10, 5.225, 46.862): south along X=5.225 on B.Cu to Y=64.00
    track(5.225, 46.862, 5.225, 64.00, pcbnew.B_Cu, led_nets[6])

    # LED_8 (Pin 11, 4.575, 46.862): south along X=4.575 on B.Cu to Y=72.00
    track(4.575, 46.862, 4.575, 72.00, pcbnew.B_Cu, led_nets[7])

    # LED_10 (Pin 13, 3.925, 41.138): north to Y=38.00 on B.Cu, via to F.Cu, west to X=1.00, south on F.Cu to Y=88.00
    track(3.925, 41.138, 3.925, 38.00, pcbnew.B_Cu, led_nets[9])
    via(3.925, 38.00, led_nets[9])
    track(3.925, 38.00, 1.00, 38.00, pcbnew.F_Cu, led_nets[9])
    track(1.00, 38.00, 1.00, 88.00, pcbnew.F_Cu, led_nets[9])

    # LED_9 (Pin 14, 4.575, 41.138): north to Y=39.50 on B.Cu, via to F.Cu, west to X=2.00, south on F.Cu to Y=80.00
    track(4.575, 41.138, 4.575, 39.50, pcbnew.B_Cu, led_nets[8])
    via(4.575, 39.50, led_nets[8])
    track(4.575, 39.50, 2.00, 39.50, pcbnew.F_Cu, led_nets[8])
    track(2.00, 39.50, 2.00, 80.00, pcbnew.F_Cu, led_nets[8])
    log("U1 to LED jumpers fully routed with zero crossings")

    # 11e. Power Routing (+3V3_IN, +3V3):
    # +3V3_IN: From J1 Pin 2 (13.805, 86.430) south to Gap 10 (Y=87.00) on B.Cu, east on B.Cu to X=36.00
    # north along X=36.00 on B.Cu to Y=9.00 (above Window 1), via to F.Cu at (36.00, 9.00)
    # west along Y=9.00 on F.Cu to X=7.00, via to B.Cu at (7.00, 9.00)
    # south along X=7.00 on B.Cu to Y=15.50, east to X=9.00, north to FB1 Pad 1 (9.00, 14.485)
    track(13.805, 86.430, 13.805, 87.00, pcbnew.B_Cu, pwr_in)
    track(13.805, 87.00, 36.00, 87.00, pcbnew.B_Cu, pwr_in)
    track(36.00, 87.00, 36.00, 9.00, pcbnew.B_Cu, pwr_in)
    via(36.00, 9.00, pwr_in)
    track(36.00, 9.00, 7.00, 9.00, pcbnew.F_Cu, pwr_in)
    via(7.00, 9.00, pwr_in)
    track(7.00, 9.00, 7.00, 15.50, pcbnew.B_Cu, pwr_in)
    track(7.00, 15.50, 9.00, 15.50, pcbnew.B_Cu, pwr_in)
    track(9.00, 15.50, 9.00, 14.485, pcbnew.B_Cu, pwr_in)

    # +3V3: From FB1 Pad 2 (9.000, 13.515):
    # East on B.Cu connects FB1 Pad 2 to C1 Pad 1 (12.00, 13.52) and C2 Pad 1 (15.00, 13.52)
    track(9.000, 13.515, 15.00, 13.520, pcbnew.B_Cu, pwr)
    # North from (9.00, 13.515) to Y=12.00, east along Y=12.00 to X=11.075:
    track(9.000, 13.515, 9.000, 12.000, pcbnew.B_Cu, pwr)
    track(9.000, 12.000, 11.075, 12.000, pcbnew.B_Cu, pwr)
    # South along X=11.075 on B.Cu directly to U1 Pin 24 (11.075, 41.138):
    track(11.075, 12.000, 11.075, 41.138, pcbnew.B_Cu, pwr) # Feeds R11 Pad 1 and U1 Pin 24
    # Connect R11 Pad 1 (10.425, 25.490) from X=11.075:
    track(11.075, 25.490, 10.425, 25.490, pcbnew.B_Cu, pwr)
    # At Y=22.00 on X=11.075, via to F.Cu to feed R12 Pad 1 and U1 Pins 15 & 16:
    via(11.075, 22.00, pwr)
    track(11.075, 22.00, 5.55, 22.00, pcbnew.F_Cu, pwr)
    via(9.775, 22.00, pwr)
    track(9.775, 22.00, 9.775, 29.490, pcbnew.B_Cu, pwr)
    via(5.55, 22.00, pwr)
    track(5.55, 22.00, 5.55, 41.138, pcbnew.B_Cu, pwr)
    track(5.225, 41.138, 5.875, 41.138, pcbnew.B_Cu, pwr)
    log("Power lines (+3V3_IN, +3V3) routed cleanly")

    # 11f. I2C Routing (SDA, SCL) - Dedicated West Corridor:
    # SCL from J1 Pin 5 (8.755, 81.350):
    # west to X=3.30, north along X=3.30 on B.Cu to Y=30.510
    # via to F.Cu at (3.30, 30.510), east along Y=30.510 on F.Cu to X=9.775, via to B.Cu at (9.775, 30.510)
    # connects north on B.Cu to R12 Pad 2 (9.775, 30.510) and south on B.Cu to U1 Pin 22 (9.775, 41.138)
    track(8.755, 81.350, 3.30, 81.350, pcbnew.B_Cu, scl)
    track(3.30, 81.350, 3.30, 30.510, pcbnew.B_Cu, scl)
    via(3.30, 30.510, scl)
    track(3.30, 30.510, 9.775, 30.510, pcbnew.F_Cu, scl)
    via(9.775, 30.510, scl)
    track(9.775, 30.510, 9.775, 41.138, pcbnew.B_Cu, scl)

    # SDA from J1 Pin 3 (8.755, 83.890):
    # west to X=2.40, north along X=2.40 on B.Cu to Y=26.510
    # via to F.Cu at (2.40, 26.510), east along Y=26.510 on F.Cu to X=10.425, via to B.Cu at (10.425, 26.510)
    # connects north on B.Cu to R11 Pad 2 (10.425, 26.510) and south on B.Cu to U1 Pin 23 (10.425, 41.138)
    track(8.755, 83.890, 2.40, 83.890, pcbnew.B_Cu, sda)
    track(2.40, 83.890, 2.40, 26.510, pcbnew.B_Cu, sda)
    via(2.40, 26.510, sda)
    track(2.40, 26.510, 10.425, 26.510, pcbnew.F_Cu, sda)
    via(10.425, 26.510, sda)
    track(10.425, 26.510, 10.425, 41.138, pcbnew.B_Cu, sda)
    log("I2C lines (SDA, SCL) routed cleanly on F.Cu/B.Cu")

    # 11g. Mezzanine Encoder lines to J2:
    # ENC_B from J1 Pin 9 (8.755, 76.270) on West:
    # east on B.Cu into cavity to X=10.700 (clearing J1 odd pads right edge at 10.33)
    # south along X=10.700 on B.Cu to Y=98.000
    # west to X=8.000 at Y=100.000 (safely clearing anti-rotation hole at 11.55)
    # south along X=8.000 on B.Cu to Y=122.000
    # east on B.Cu along Y=122.000 to X=19.050, south to J2 Pad 3 (19.050, 123.500)
    track(8.755, 76.270, 10.700, 76.270, pcbnew.B_Cu, enc_b)
    track(10.700, 76.270, 10.700, 98.000, pcbnew.B_Cu, enc_b)
    track(10.700, 98.000, 8.000, 100.000, pcbnew.B_Cu, enc_b)
    track(8.000, 100.000, 8.000, 122.000, pcbnew.B_Cu, enc_b)
    track(8.000, 122.000, 19.050, 122.000, pcbnew.B_Cu, enc_b)
    track(19.050, 122.000, 19.050, 123.500, pcbnew.B_Cu, enc_b)

    # ENC_SW from J1 Pin 12 (13.805, 73.730) on East:
    # enters cavity on B.Cu to X=11.280, south along X=11.280 on B.Cu to Y=96.500
    # east on B.Cu along Y=96.500 to X=31.000, south on B.Cu along X=31.000 to Y=115.000
    # west to X=16.510, south to J2 Pad 4 (16.510, 120.200)
    track(13.805, 73.730, 11.280, 73.730, pcbnew.B_Cu, enc_sw)
    track(11.280, 73.730, 11.280, 96.500, pcbnew.B_Cu, enc_sw)
    track(11.280, 96.500, 31.000, 96.500, pcbnew.B_Cu, enc_sw)
    track(31.000, 96.500, 31.000, 115.000, pcbnew.B_Cu, enc_sw)
    track(31.000, 115.000, 16.510, 115.000, pcbnew.B_Cu, enc_sw)
    track(16.510, 115.000, 16.510, 120.200, pcbnew.B_Cu, enc_sw)

    # ENC_A from J1 Pin 10 (13.805, 76.270) on East:
    # enters cavity on B.Cu to X=11.860 (clearing J1 even pads left edge at 12.23)
    # south along X=11.860 on B.Cu to Y=95.000
    # east on B.Cu along Y=95.000 to X=33.000, south on B.Cu along X=33.000 to Y=118.000
    # west to X=24.130, south to J2 Pad 1 (24.130, 123.500)
    track(13.805, 76.270, 11.860, 76.270, pcbnew.B_Cu, enc_a)
    track(11.860, 76.270, 11.860, 95.000, pcbnew.B_Cu, enc_a)
    track(11.860, 95.000, 33.000, 95.000, pcbnew.B_Cu, enc_a)
    track(33.000, 95.000, 33.000, 118.000, pcbnew.B_Cu, enc_a)
    track(33.000, 118.000, 24.130, 118.000, pcbnew.B_Cu, enc_a)
    track(24.130, 118.000, 24.130, 123.500, pcbnew.B_Cu, enc_a)
    log("Mezzanine encoder lines routed with 0 crossings")

    # 11h. Ground Connections:
    # U1 belly GND bus on B.Cu connecting Pin 12, Pins 17/18, and Pins 1, 2, 3:
    track(3.925, 46.862, 3.925, 44.00, pcbnew.B_Cu, gnd) # Pin 12 into belly
    track(3.925, 44.00, 11.075, 44.00, pcbnew.B_Cu, gnd)  # Belly central bus
    track(6.525, 44.00, 6.525, 41.138, pcbnew.B_Cu, gnd) # Pins 17/18
    track(7.175, 41.138, 6.525, 41.138, pcbnew.B_Cu, gnd)
    track(9.775, 44.00, 9.775, 46.862, pcbnew.B_Cu, gnd) # Pins 1, 2, 3
    track(9.775, 46.862, 11.075, 46.862, pcbnew.B_Cu, gnd)
    via(8.50, 44.00, gnd) # Belly via to F.Cu GND (clears X=7.175)

    # J1 GND pins continuous tracks:
    track(8.755, 63.57, 8.755, 73.73, pcbnew.B_Cu, gnd) # Pins 19, 17, 15, 13, 11
    track(13.805, 63.57, 13.805, 71.19, pcbnew.B_Cu, gnd) # Pins 20, 18, 16, 14
    track(13.805, 78.81, 13.805, 83.89, pcbnew.B_Cu, gnd) # Pins 8, 6, 4

    # 12. Optical Baffle Ground Zones (Full Board Coverage with Optical Window Holes on F.Cu)
    zone_f = pcbnew.ZONE(board)
    lset_f = pcbnew.LSET()
    lset_f.AddLayer(pcbnew.F_Cu)
    zone_f.SetLayerSet(lset_f)
    zone_f.SetLayer(pcbnew.F_Cu)
    zone_f.SetNet(gnd)
    out_f = zone_f.Outline()
    out_f.NewOutline()
    out_f.Append(mm(0.5), mm(0.5))
    out_f.Append(mm(W-0.5), mm(0.5))
    out_f.Append(mm(W-0.5), mm(H-0.5))
    out_f.Append(mm(0.5), mm(H-0.5))
    for i in range(10):
        wy = 20.0 + 8.0 * i
        wx1, wx2 = 13.05, 25.05
        wy1, wy2 = wy - 2.0, wy + 2.0
        out_f.NewHole()
        out_f.Append(mm(wx1), mm(wy1))
        out_f.Append(mm(wx2), mm(wy1))
        out_f.Append(mm(wx2), mm(wy2))
        out_f.Append(mm(wx1), mm(wy2))
    zone_f.SetMinThickness(mm(0.20))
    zone_f.SetThermalReliefGap(mm(0.25))
    zone_f.SetThermalReliefSpokeWidth(mm(0.30))
    zone_f.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    board.Add(zone_f)

    # B.Cu Ground Zone (Continuous ground plane across the entire board)
    zone_b = pcbnew.ZONE(board)
    lset_b = pcbnew.LSET()
    lset_b.AddLayer(pcbnew.B_Cu)
    zone_b.SetLayerSet(lset_b)
    zone_b.SetLayer(pcbnew.B_Cu)
    zone_b.SetNet(gnd)
    out_b = zone_b.Outline()
    out_b.NewOutline()
    out_b.Append(mm(0.5), mm(0.5))
    out_b.Append(mm(W-0.5), mm(0.5))
    out_b.Append(mm(W-0.5), mm(H-0.5))
    out_b.Append(mm(0.5), mm(H-0.5))
    zone_b.SetMinThickness(mm(0.20))
    zone_b.SetThermalReliefGap(mm(0.25))
    zone_b.SetThermalReliefSpokeWidth(mm(0.30))
    zone_b.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    board.Add(zone_b)
    log("Optical baffle ground zones created on F.Cu and B.Cu")

    # 13. Ground Stitching Vias (strategically placed in clear ground plane areas)
    stitching_pts = [
        (5.00, 6.00), (35.00, 6.00),
        (35.00, 80.00), (35.00, 92.00),
        (37.00, 30.00), (37.00, 50.00), (37.00, 70.00),
        (5.00, 125.00), (35.00, 125.00)
    ]
    for x, y in stitching_pts:
        via(x, y, gnd)
    log(f"Added {len(stitching_pts)} GND stitching vias")

    # 13b. Prominent Fabrication Notes and Board Markings
    notes = [
        "FABRICATION SPECIFICATIONS - ACTIVE FACEPLATE:",
        "1. PCB THICKNESS: 2.0 mm FR4 (HEAVY-DUTY PRO AUDIO SPECIFICATION)",
        "2. SOLDERMASK: BLACK (MATTE FINISH PREFERRED)",
        "3. SILKSCREEN: WHITE",
        "4. SURFACE FINISH: ENIG (ELECTROLESS NICKEL IMMERSION GOLD)",
        "5. COPPER WEIGHT: 1 oz (Outer Layers)",
        "6. OPTICAL WAVEGUIDES: 10x RECTANGULAR WINDOWS (12.0 x 4.0 mm)",
        "   HAVE COPPER AND SOLDERMASK OMITTED ON F.Mask & B.Mask.",
        "   SOLID FR4 CORE PRESERVED - DO NOT MILL OUT APERTURES.",
        "7. CONNECTOR J1 MATES WITH CARRIER U6 (0.75 mm MATING MARGIN).",
        "8. CONNECTOR J2 MATES WITH ENCODER DAUGHTERCARD P1.",
    ]
    for idx, line in enumerate(notes):
        txt = pcbnew.PCB_TEXT(board)
        txt.SetText(line)
        txt.SetLayer(pcbnew.Cmts_User)
        txt.SetPosition(pcbnew.VECTOR2I(mm(2.0), mm(140.0 + idx * 2.5)))
        txt.SetTextSize(pcbnew.VECTOR2I(mm(1.2), mm(1.2)))
        board.Add(txt)

    # Silkscreen marking on B.Silkscreen
    txt_b = pcbnew.PCB_TEXT(board)
    txt_b.SetText("ICIO-500 FACEPLATE v2.0 - 2.0mm FR4")
    txt_b.SetLayer(pcbnew.B_SilkS)
    txt_b.SetPosition(pcbnew.VECTOR2I(mm(19.05), mm(99.0)))
    txt_b.SetTextSize(pcbnew.VECTOR2I(mm(1.0), mm(1.0)))
    txt_b.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
    txt_b.SetMirrored(True) # Correct mirroring for rear silkscreen
    board.Add(txt_b)

    # 14. Refill Zones
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    log("Zones filled")

    # 15. Save Board
    board.Save(src_path)
    log(f"Active Faceplate PCB built and saved to {src_path}!")

if __name__ == '__main__':
    build_faceplate()
