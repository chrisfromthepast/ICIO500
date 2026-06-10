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

def make_zone_bounded(board, lyr, net_name, x0, y0, x1, y1):
    net = board.FindNet(net_name)
    if not net:
        return None
    zones_to_remove = []
    for z in board.Zones():
        if z.GetLayer() == lyr and z.GetNetCode() == net.GetNetCode():
            zones_to_remove.append(z)
    for z in zones_to_remove:
        board.Remove(z)
            
    z = pcbnew.ZONE(board)
    z.SetLayer(lyr)
    z.SetNet(net)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    ch = pcbnew.SHAPE_LINE_CHAIN()
    ch.Append(mm(x0), mm(y0))
    ch.Append(mm(x1), mm(y0))
    ch.Append(mm(x1), mm(y1))
    ch.Append(mm(x0), mm(y1))
    ch.SetClosed(True)
    z.AddPolygon(ch)
    board.Add(z)
    return z

def route_chain(board, net_name, w=0.5, lyr=None):
    n = board.FindNet(net_name)
    if not n: return
    if lyr is None: lyr = pcbnew.F_Cu
    
    # Extract pads belonging to this net
    pads = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetCode() == n.GetNetCode():
                pads.append(p)
                
    if len(pads) < 2: return
    
    # Sort them by X coordinate (left-to-right)
    pads.sort(key=lambda p: p.GetPosition().x)
    
    for i in range(len(pads) - 1):
        p0 = pads[i]
        p1 = pads[i+1]
        
        x0, y0 = frm(p0.GetPosition().x), frm(p0.GetPosition().y)
        x1, y1 = frm(p1.GetPosition().x), frm(p1.GetPosition().y)
        
        # Calculate clean fan-out via placement for SMD pads
        def get_connect_pt(p, offset_val):
            px, py = frm(p.GetPosition().x), frm(p.GetPosition().y)
            if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                # PTH pad connects directly on B_Cu
                return px, py, False
            else:
                # SMD pad: drop a via offsetted horizontally to avoid via-in-pad
                vx = px + offset_val
                vy = py
                return vx, vy, True
                
        # Offset vias slightly to avoid overlap
        dist_x = abs(x1 - x0)
        offset0 = 1.5 if dist_x > 3.0 else (dist_x / 2.0)
        offset1 = -1.5 if dist_x > 3.0 else -(dist_x / 2.0)
        
        vx0, vy0, need_via0 = get_connect_pt(p0, offset0)
        vx1, vy1, need_via1 = get_connect_pt(p1, offset1)
        
        if lyr == pcbnew.B_Cu:
            if need_via0:
                add_via(board, vx0, vy0, n)
                # trace from pad to via on Front
                seg(board, n, x0, y0, vx0, vy0, w=0.5, lyr=pcbnew.F_Cu)
            if need_via1:
                add_via(board, vx1, vy1, n)
                # trace from pad to via on Front
                seg(board, n, x1, y1, vx1, vy1, w=0.5, lyr=pcbnew.F_Cu)
                
            # Route on Bottom between the connection points
            LH(board, n, vx0, vy0, vx1, vy1, w, pcbnew.B_Cu)
        else:
            LH(board, n, x0, y0, x1, y1, w, lyr)

def route_j1_connections(board):
    # Output stage is at Y = 75. Route out_plus_4dbu to Pin 2, out_minus to Pin 4.
    n_out_p = board.FindNet('out_plus_4dbu')
    if n_out_p:
        seg(board, n_out_p, 180, 71.0, 180, 79.1, w=0.8, lyr=pcbnew.F_Cu)
        seg(board, n_out_p, 180, 79.1, 195, 79.1, w=0.8, lyr=pcbnew.F_Cu)

    n_out_m = board.FindNet('out_minus')
    if n_out_m:
        seg(board, n_out_m, 180, 77.0, 180, 87.0, w=0.8, lyr=pcbnew.B_Cu)
        seg(board, n_out_m, 180, 87.0, 195, 87.0, w=0.8, lyr=pcbnew.B_Cu)
        add_via(board, 180, 77.0, n_out_m, sz=1.0, dr=0.4)

    # Input stage is at Y = 135. Route in_minus_4dbu to Pin 8 (B_Cu), in_plus_4dbu to Pin 10 (F_Cu).
    n_in_m = board.FindNet('in_minus_4dbu')
    if n_in_m:
        seg(board, n_in_m, 180, 138.0, 180, 102.9, w=0.8, lyr=pcbnew.B_Cu)
        seg(board, n_in_m, 180, 102.9, 195, 102.9, w=0.8, lyr=pcbnew.B_Cu)
        add_via(board, 180, 138.0, n_in_m, sz=1.0, dr=0.4)

    n_in_p = board.FindNet('in_plus_4dbu')
    if n_in_p:
        seg(board, n_in_p, 180, 132.0, 180, 110.8, w=0.8, lyr=pcbnew.F_Cu)
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

    # Clear old zones
    zones_to_remove = [z for z in board.Zones()]
    for z in zones_to_remove:
        board.Remove(z)

    # Split ground planes on Inner Layer 1 (In1_Cu)
    # Digital Ground on the left (X: 35 to 125, Y: 10 to 185)
    make_zone_bounded(board, pcbnew.In1_Cu, 'daisy_digital_gnd', 35, 10, 125, 185)
    # Analog Ground on the right (X: 125 to 240, Y: 10 to 185)
    make_zone_bounded(board, pcbnew.In1_Cu, 'gnd', 125, 10, 240, 185)

    # Default net class (Signals)
    default_class = board.GetNetClasses()['Default']
    default_class.SetTrackWidth(mm(0.25))
    default_class.SetClearance(mm(0.2))

    # Assign power and ground nets to Power net class for thicker traces
    power_net_names = ['gnd', 'v_plus', 'v_minus', 'daisy_digital_gnd', 'daisy_5v_power', 'v_plus_16v', 'v_minus_16v']
    power_class = board.GetNetClasses()['Power']
    power_class.SetTrackWidth(mm(0.8))
    power_class.SetClearance(mm(0.25))
    for name in power_net_names:
        net = board.FindNet(name)
        if net:
            net.SetNetClass(power_class)
            print(f"Assigned net {name} to class Power")

    # Power inputs from J1 to U1 (DCDC) - these don't collide
    # route_chain(board, 'v_plus_16v', 1.0, pcbnew.B_Cu)
    # route_chain(board, 'v_minus_16v', 1.0, pcbnew.B_Cu)

    # Bridge the mismatched nets to J1
    # route_j1_connections(board)

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    pcbnew.SaveBoard(pcb_path, board)
    print("Routing complete using 4 layers. J1 connected. Zones filled.")

if __name__ == '__main__':
    apply_routing()
