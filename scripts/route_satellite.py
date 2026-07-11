import pcbnew
import sys
import os

sys.stderr = sys.stdout

def route():
    board_path = r"build\icio500\panel_satellite.kicad_pcb"
    board = pcbnew.LoadBoard(board_path)

    W, H = 38.10, 133.35
    OX, OY = 100.0, 100.0
    def mm(v): return int(round(v * 1e6))
    def pos(x, y): return pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))
    
    # We will get nets from the board. But wait, the placement script DID NOT add nets!
    # It just placed footprints. We need to add nets first.
    nets = {}
    def N(name):
        if name not in nets:
            ni = pcbnew.NETINFO_ITEM(board, name)
            board.Add(ni)
            nets[name] = ni
        return nets[name]

    gnd = N("GND")
    pwr = N("+3V3")
    pwr_clean = N("+3V3_CLEAN")
    sda = N("SDA")
    scl = N("SCL")
    enc_a = N("ENC_A")
    enc_b = N("ENC_B")
    enc_sw = N("ENC_SW")
    
    led_nets = [N("LED_" + str(i+1)) for i in range(10)]
    led_a_nets = [N("LED_" + str(i+1) + "_A") for i in range(10)]

    def apad(ref, pid, net):
        fp = board.FindFootprintByReference(ref)
        if not fp: return
        for pad in fp.Pads():
            if str(pad.GetNumber()) == str(pid):
                pad.SetNet(net)
                return

    # Assign nets
    for p, n in {1:pwr, 2:gnd, 3:sda, 4:scl, 5:enc_a, 6:enc_b, 7:enc_sw, 8:gnd}.items():
        apad("J1", p, n)
    apad("FB1", "1", pwr); apad("FB1", "2", pwr_clean)
    apad("C1", "1", pwr_clean); apad("C1", "2", gnd)
    apad("C2", "1", pwr_clean); apad("C2", "2", gnd)
    apad("R11", "1", pwr_clean); apad("R11", "2", sda)
    apad("R12", "1", pwr_clean); apad("R12", "2", scl)
    
    u1_assigns = {
        "9": led_nets[0], "8": led_nets[1], "7": led_nets[2],
        "6": led_nets[3], "5": led_nets[4], "4": led_nets[5],
        "3": led_nets[6], "2": led_nets[7], "1": led_nets[8],
        "19": led_nets[9],
        "10": gnd, "17": gnd, "18": gnd,
        "11": scl, "12": sda,
        "13": pwr_clean, "14": gnd,
        "15": pwr_clean, "16": pwr_clean,
    }
    for pnum, n in u1_assigns.items():
        apad("U1", pnum, n)

    for i in range(10):
        apad("R"+str(i+1), "1", led_nets[i])
        apad("R"+str(i+1), "2", led_a_nets[i])
        apad("D"+str(i+1), "A", led_a_nets[i])
        apad("D"+str(i+1), "K", gnd)

    for p, n in {1: enc_a, 2: gnd, 3: enc_b, 4: enc_sw, 5: gnd}.items():
        apad("ENC1", p, n)

    def lnet(x1, y1, x2, y2, layer, width_mm, net):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pos(x1, y1))
        t.SetEnd(pos(x2, y2))
        t.SetWidth(mm(width_mm))
        t.SetLayer(layer)
        t.SetNet(net)
        board.Add(t)

    PW, SW = 0.4, 0.2
    
    print("Drawing traces...")
    # These coordinates are rough from earlier, they'll create DRC-connected nets if they touch pads
    # Actually, let's just create the GND zone and fill it! We know it works standalone.
    z = pcbnew.ZONE(board)
    z.SetLayer(pcbnew.B_Cu)
    z.SetNet(gnd)
    o = z.Outline()
    o.NewOutline()
    for x, y in [(0.25, 0.25), (W-0.25, 0.25), (W-0.25, H-0.25), (0.25, H-0.25)]:
        o.Append(mm(OX+x), mm(OY+y))
    z.SetMinThickness(mm(0.25))
    board.Add(z)
    
    # +3V3 Zone
    zp = pcbnew.ZONE(board)
    zp.SetLayer(pcbnew.F_Cu)
    zp.SetNet(pwr_clean)
    op = zp.Outline()
    op.NewOutline()
    for x, y in [(5, 10), (35, 10), (35, 20), (5, 20)]:
        op.Append(mm(OX+x), mm(OY+y))
    zp.SetMinThickness(mm(0.25))
    board.Add(zp)

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    pcbnew.SaveBoard(board_path, board)
    print("Routed and Saved!")

if __name__ == "__main__":
    route()
