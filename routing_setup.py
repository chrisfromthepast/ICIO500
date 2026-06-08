"""
routing_setup.py – ICIO500 4-layer routing (Full Pass including J1)
====================================================================
"""

import pcbnew, os
import sys

def mm(v):   return int(v * 1_000_000)
def frm(iu): return iu / 1_000_000.0

def seg(board, net, x0, y0, x1, y1, w=0.5, lyr=None):
    if lyr is None: lyr = pcbnew.F_Cu
    if abs(x0-x1) < 0.01 and abs(y0-y1) < 0.01:
        return
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(mm(x0), mm(y0)))
    t.SetEnd(  pcbnew.VECTOR2I(mm(x1), mm(y1)))
    t.SetWidth(mm(w))
    t.SetLayer(lyr)
    if net:
        t.SetNet(net)
    board.Add(t)

def LH(board, net, x0, y0, x1, y1, w=0.5, lyr=None):
    seg(board, net, x0, y0, x1, y0, w, lyr)
    seg(board, net, x1, y0, x1, y1, w, lyr)

def add_via(board, x, y, net, sz=1.0, dr=0.4):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    v.SetWidth(mm(sz))
    v.SetDrill(mm(dr))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    if net:
        v.SetNet(net)
    board.Add(v)

def make_zone(board, lyr, net_name):
    net = board.FindNet(net_name)
    if not net:
        return None
    for z in board.Zones():
        if z.GetLayer() == lyr and z.GetNetCode() == net.GetNetCode():
            return z  # already exists
            
    z = pcbnew.ZONE(board)
    z.SetLayer(lyr)
    z.SetNet(net)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    bbox = board.ComputeBoundingBox()
    ch = pcbnew.SHAPE_LINE_CHAIN()
    ch.Append(bbox.GetX() - mm(5),     bbox.GetY() - mm(5))
    ch.Append(bbox.GetRight() + mm(5), bbox.GetY() - mm(5))
    ch.Append(bbox.GetRight() + mm(5), bbox.GetBottom() + mm(5))
    ch.Append(bbox.GetX() - mm(5),     bbox.GetBottom() + mm(5))
    ch.SetClosed(True)
    z.AddPolygon(ch)
    board.Add(z)
    return z

def net_pads(board, net_name):
    n = board.FindNet(net_name)
    if not n: return []
    pts = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetCode() == n.GetNetCode():
                pos = p.GetPosition()
                pts.append((frm(pos.x), frm(pos.y)))
    pts.sort()
    return pts

def route_chain(board, net_name, w=0.5, lyr=None):
    n = board.FindNet(net_name)
    if not n: return
    if lyr is None: lyr = pcbnew.F_Cu
    pts = net_pads(board, net_name)
    if len(pts) < 2: return
    
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        
        if lyr == pcbnew.B_Cu:
            add_via(board, x0, y0, n)
            add_via(board, x1, y1, n)
            
        LH(board, n, x0, y0, x1, y1, w, lyr)

def route_j1_connections(board):
    n_out_p = board.FindNet('out_plus_4dbu')
    if n_out_p:
        seg(board, n_out_p, 180, 85, 180, 79.1, w=0.8, lyr=pcbnew.F_Cu)
        seg(board, n_out_p, 180, 79.1, 195, 79.1, w=0.8, lyr=pcbnew.F_Cu)

    n_out_m = board.FindNet('out_minus')
    if n_out_m:
        seg(board, n_out_m, 180, 89, 180, 87.0, w=0.8, lyr=pcbnew.B_Cu)
        seg(board, n_out_m, 180, 87.0, 195, 87.0, w=0.8, lyr=pcbnew.B_Cu)

    n_in_m = board.FindNet('in_minus_4dbu')
    if n_in_m:
        seg(board, n_in_m, 180, 100, 180, 102.9, w=0.8, lyr=pcbnew.F_Cu)
        seg(board, n_in_m, 180, 102.9, 195, 102.9, w=0.8, lyr=pcbnew.F_Cu)

    n_in_p = board.FindNet('in_plus_4dbu')
    if n_in_p:
        seg(board, n_in_p, 180, 104, 180, 110.8, w=0.8, lyr=pcbnew.F_Cu)
        seg(board, n_in_p, 180, 110.8, 195, 110.8, w=0.8, lyr=pcbnew.F_Cu)

    n_p16 = board.FindNet('+16V')
    if n_p16:
        seg(board, n_p16, 195, 118.7, 160, 118.7, w=1.2, lyr=pcbnew.B_Cu)
        seg(board, n_p16, 160, 118.7, 160, 108.0, w=1.2, lyr=pcbnew.B_Cu)
        seg(board, n_p16, 160, 108.0, 155, 108.0, w=1.2, lyr=pcbnew.B_Cu)
        add_via(board, 155, 108.0, n_p16, sz=1.2, dr=0.6)

    n_m16 = board.FindNet('-16V')
    if n_m16:
        seg(board, n_m16, 195, 126.6, 165, 126.6, w=1.2, lyr=pcbnew.B_Cu)
        seg(board, n_m16, 165, 126.6, 165, 116.0, w=1.2, lyr=pcbnew.B_Cu)
        seg(board, n_m16, 165, 116.0, 155, 116.0, w=1.2, lyr=pcbnew.B_Cu)
        add_via(board, 155, 116.0, n_m16, sz=1.2, dr=0.6)

    n_gnd = board.FindNet('GND')
    if n_gnd:
        add_via(board, 193, 122.7, n_gnd, sz=1.5, dr=0.8)

    n_chas = board.FindNet('/CHASSIS')
    if n_chas:
        add_via(board, 193, 75.1, n_chas, sz=1.5, dr=0.8)

def apply_routing():
    pcb_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "build", "icio500", "icio500.kicad_pcb"
    )
    board = pcbnew.LoadBoard(pcb_path)
    print("Board loaded.")
    sys.stdout.flush()

    # Clear old tracks
    old_tracks = list(board.Tracks())
    for t in old_tracks:
        board.Remove(t)

    # Power planes
    make_zone(board, pcbnew.In1_Cu, 'gnd')
    make_zone(board, pcbnew.In2_Cu, 'v_plus')
    make_zone(board, pcbnew.B_Cu,   'v_minus')
    make_zone(board, pcbnew.In1_Cu, 'daisy_digital_gnd') # Will fill remaining space or require boundary
    
    # Drop vias for power pads
    power_nets = ['gnd', 'v_plus', 'v_minus', 'daisy_digital_gnd', 'chassis']
    for net_name in power_nets:
        n = board.FindNet(net_name)
        if not n: continue
        for fp in board.GetFootprints():
            for p in fp.Pads():
                if p.GetNetCode() == n.GetNetCode():
                    pos = p.GetPosition()
                    add_via(board, frm(pos.x), frm(pos.y), n, sz=1.0, dr=0.4)

    # Route Signal Nets inside the IO block
    W = 0.5
    route_chain(board, 'in_plus',  W, pcbnew.F_Cu)
    route_chain(board, 'in_minus', W, pcbnew.F_Cu)
    route_chain(board, 'in_plus_4dbu',  W, pcbnew.F_Cu)
    route_chain(board, 'in_minus_4dbu', W, pcbnew.F_Cu)
    route_chain(board, 'cm', W, pcbnew.F_Cu)
    route_chain(board, 'sm', W, pcbnew.F_Cu)
    route_chain(board, 'audio_out', W, pcbnew.F_Cu)
    route_chain(board, 'in_minus_1', W, pcbnew.F_Cu)
    
    route_chain(board, 'receiver.r_rf_plus-vcc', W, pcbnew.F_Cu)
    route_chain(board, 'receiver.r_rf_minus-vcc', W, pcbnew.F_Cu)
    route_chain(board, 'v_bias_2v5', W, pcbnew.F_Cu)
    route_chain(board, 'driver.r_zobel_plus-vcc', W, pcbnew.F_Cu)
    route_chain(board, 'driver.r_zobel_minus-vcc', W, pcbnew.F_Cu)
    
    route_chain(board, 'receiver.c_rf_plus_chas-vcc', W, pcbnew.F_Cu)
    route_chain(board, 'receiver.c_rf_minus_chas-vcc', W, pcbnew.F_Cu)

    route_chain(board, 'audio_out_to_1646', W, pcbnew.B_Cu)
    route_chain(board, 'in_minus_2', W, pcbnew.B_Cu)
    route_chain(board, 'out_plus_4dbu', W, pcbnew.B_Cu)
    route_chain(board, 'out_minus', W, pcbnew.B_Cu)
    route_chain(board, 'sense_plus', W, pcbnew.B_Cu)
    route_chain(board, 'sense_minus', W, pcbnew.B_Cu)
    
    route_chain(board, 'daisy_audio_in', W, pcbnew.F_Cu)
    route_chain(board, 'daisy_audio_out', W, pcbnew.B_Cu)
    route_chain(board, 'daisy_5v_power', 1.0, pcbnew.B_Cu)

    # Bridge the mismatched nets to J1
    route_j1_connections(board)

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    pcbnew.SaveBoard(pcb_path, board)
    print("Routing complete using 4 layers. J1 connected. Zones filled.")

if __name__ == '__main__':
    apply_routing()
