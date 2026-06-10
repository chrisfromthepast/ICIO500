"""
routing_j1.py – ICIO500 J1 connector routing
=============================================
This script routes the remaining connections from the tightly packed IO block 
to the J1 card edge connector, bridging the netlist naming gaps.
"""

import pcbnew, os

def mm(v):   return int(v * 1_000_000)
def frm(iu): return iu / 1_000_000.0

def add_track(board, x0, y0, x1, y1, net=None, w=0.5, lyr=None):
    if lyr is None: lyr = pcbnew.F_Cu
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(mm(x0), mm(y0)))
    t.SetEnd(  pcbnew.VECTOR2I(mm(x1), mm(y1)))
    t.SetWidth(mm(w))
    t.SetLayer(lyr)
    if net:
        t.SetNet(net)
    board.Add(t)

def add_via(board, x, y, net, sz=1.0, dr=0.4):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    v.SetWidth(mm(sz))
    v.SetDrill(mm(dr))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    if net:
        v.SetNet(net)
    board.Add(v)

def apply_j1_routing():
    pcb_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "build", "icio500", "icio500.kicad_pcb"
    )
    board = pcbnew.LoadBoard(pcb_path)
    
    # We will draw explicit tracks to J1 pads.
    # J1 pad X coordinates: the gold fingers start around 194.5 and go to 202.5.
    # We'll target X = 195.0 to attach to the inner tip of the fingers.
    
    # 1. Output Plus (J1 Pin 2, Y=79.1) -> D3 (X=180, Y=85) and U5 output
    n_out_p = board.FindNet('out_plus_4dbu')
    if n_out_p:
        # Route from D3 pad 2 to J1 pin 2
        add_track(board, 180, 85, 180, 79.1, n_out_p, w=0.8, lyr=pcbnew.F_Cu)
        add_track(board, 180, 79.1, 195, 79.1, n_out_p, w=0.8, lyr=pcbnew.F_Cu)

    # 2. Output Minus (J1 Pin 4, Y=87.0) -> D4 (X=180, Y=89)
    n_out_m = board.FindNet('out_minus')
    if n_out_m:
        add_track(board, 180, 89, 180, 87.0, n_out_m, w=0.8, lyr=pcbnew.B_Cu)
        add_track(board, 180, 87.0, 195, 87.0, n_out_m, w=0.8, lyr=pcbnew.B_Cu)

    # 3. Input Minus (J1 Pin 8, Y=102.9) -> D5 (X=180, Y=100) and R2
    n_in_m = board.FindNet('in_minus_4dbu')
    if n_in_m:
        add_track(board, 180, 100, 180, 102.9, n_in_m, w=0.8, lyr=pcbnew.F_Cu)
        add_track(board, 180, 102.9, 195, 102.9, n_in_m, w=0.8, lyr=pcbnew.F_Cu)

    # 4. Input Plus (J1 Pin 10, Y=110.8) -> D6 (X=180, Y=104) and R1
    n_in_p = board.FindNet('in_plus_4dbu')
    if n_in_p:
        add_track(board, 180, 104, 180, 110.8, n_in_p, w=0.8, lyr=pcbnew.F_Cu)
        add_track(board, 180, 110.8, 195, 110.8, n_in_p, w=0.8, lyr=pcbnew.F_Cu)

    # 5. Power Rails
    # +16V (J1 Pin 12, Y=118.7) -> D1 Anode
    # D1 is at X=155, Y=108. Anode is pad 2.
    # Let's drop a via at J1 pin 12 and route on B.Cu to D1
    n_p16 = board.FindNet('+16V')
    if n_p16:
        # Route from J1 pin 12 to X=160
        add_track(board, 195, 118.7, 160, 118.7, n_p16, w=1.2, lyr=pcbnew.B_Cu)
        add_track(board, 160, 118.7, 160, 108.0, n_p16, w=1.2, lyr=pcbnew.B_Cu)
        add_track(board, 160, 108.0, 155, 108.0, n_p16, w=1.2, lyr=pcbnew.B_Cu)
        # Drop via at D1
        add_via(board, 155, 108.0, n_p16, sz=1.2, dr=0.6)

    # -16V (J1 Pin 14, Y=126.6) -> D2 Cathode
    # D2 is at X=155, Y=116. Cathode is pad 1.
    n_m16 = board.FindNet('-16V')
    if n_m16:
        add_track(board, 195, 126.6, 165, 126.6, n_m16, w=1.2, lyr=pcbnew.B_Cu)
        add_track(board, 165, 126.6, 165, 116.0, n_m16, w=1.2, lyr=pcbnew.B_Cu)
        add_track(board, 165, 116.0, 155, 116.0, n_m16, w=1.2, lyr=pcbnew.B_Cu)
        add_via(board, 155, 116.0, n_m16, sz=1.2, dr=0.6)

    # 6. GND (J1 Pin 13, Y=122.7) -> GND Plane
    # Just drop a via directly at the pin!
    n_gnd = board.FindNet('GND')
    if n_gnd:
        add_via(board, 193, 122.7, n_gnd, sz=1.5, dr=0.8)

    # 7. CHASSIS GND (J1 Pin 1, Y=75.1) -> GND Plane
    n_chas = board.FindNet('/CHASSIS')
    if n_chas:
        add_via(board, 193, 75.1, n_chas, sz=1.5, dr=0.8)

    pcbnew.SaveBoard(pcb_path, board)
    print("J1 connections routed!")

if __name__ == '__main__':
    apply_j1_routing()
