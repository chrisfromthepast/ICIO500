import pcbnew
import os

MM = 1e6
def mm(v): return int(round(v * MM))

def build_encoder_board():
    board = pcbnew.BOARD()
    
    W = 20.0
    H = 26.0
    
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(mm(1.6))
    ds.m_CopperEdgeClearance = mm(0.35)
    ds.m_TrackClearance = mm(0.20)
    
    # Edge.Cuts
    pts = [(0.0, 0.0), (W, 0.0), (W, H), (0.0, H)]
    for i in range(4):
        p1 = pts[i]
        p2 = pts[(i+1)%4]
        line = pcbnew.PCB_SHAPE(board)
        line.SetShape(pcbnew.SHAPE_T_SEGMENT)
        line.SetStart(pcbnew.VECTOR2I(mm(p1[0]), mm(p1[1])))
        line.SetEnd(pcbnew.VECTOR2I(mm(p2[0]), mm(p2[1])))
        line.SetLayer(pcbnew.Edge_Cuts)
        line.SetWidth(mm(0.15))
        board.Add(line)
        
    nets = {}
    def N(name):
        if name not in nets:
            ni = pcbnew.NETINFO_ITEM(board, name)
            board.Add(ni)
            nets[name] = ni
        return nets[name]
        
    gnd = N("GND")
    enc_a = N("ENC_A")
    enc_b = N("ENC_B")
    enc_sw = N("ENC_SW")
    
    enc_lib = r'C:\Program Files\KiCad\10.0\share\kicad\footprints\Rotary_Encoder.pretty'
    hdr_lib = r'C:\Program Files\KiCad\10.0\share\kicad\footprints\Connector_PinSocket_2.54mm.pretty'
    
    # ENC1 at x0=2.5, y0=7.5 -> Shaft center at (10.0, 10.0)
    enc_fp = pcbnew.FootprintLoad(enc_lib, 'RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm')
    enc_fp.SetReference('ENC1')
    enc_fp.SetValue('PEC11R-4020F-S0024')
    enc_fp.SetPosition(pcbnew.VECTOR2I(mm(2.5), mm(7.5)))
    if enc_fp.Models():
        step_path = os.path.abspath('build/icio500/RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm.step')
        if os.path.exists(step_path):
            enc_fp.Models()[0].m_Filename = step_path
    board.Add(enc_fp)
    
    for pad in enc_fp.Pads():
        num = str(pad.GetNumber())
        if num in ('A', '1'):
            pad.SetNet(enc_a)
        elif num in ('B', '3'):
            pad.SetNet(enc_b)
        elif num in ('C', '2'):
            pad.SetNet(gnd)
        elif num in ('S1', '4'):
            pad.SetNet(enc_sw)
        elif num in ('S2', '5'):
            pad.SetNet(gnd)
        elif 'MP' in num:
            pad.SetNet(gnd)
            
    # P1: 1x5 Horizontal female socket at bottom (Y = 22.5 mm)
    # Origin is Pad 1. Set at X = 4.5 mm, Y = 22.5 mm, orientation 90 deg (horizontal)
    # Pads 1..5 will be at X = 4.50, 7.04, 9.58, 12.12, 14.66 mm (all perfectly centered with > 5mm margin!)
    p1_fp = pcbnew.FootprintLoad(hdr_lib, 'PinSocket_1x05_P2.54mm_Vertical')
    p1_fp.SetReference('P1')
    p1_fp.SetValue('Conn_01x05_Female')
    p1_fp.SetPosition(pcbnew.VECTOR2I(mm(4.5), mm(22.5)))
    p1_fp.SetOrientation(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
    board.Add(p1_fp)
    
    p1_map = {'1': enc_a, '2': enc_b, '3': gnd, '4': enc_sw, '5': gnd}
    for pad in p1_fp.Pads():
        num = str(pad.GetNumber())
        if num in p1_map:
            pad.SetNet(p1_map[num])

    pads_enc = {str(p.GetNumber()): (p.GetPosition().x/MM, p.GetPosition().y/MM) for p in enc_fp.Pads()}
    pads_p1 = {str(p.GetNumber()): (p.GetPosition().x/MM, p.GetPosition().y/MM) for p in p1_fp.Pads()}

    def add_track(x1, y1, x2, y2, layer, net, width=0.25):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
        t.SetLayer(layer)
        t.SetNet(net)
        t.SetWidth(mm(width))
        board.Add(t)

    # Route ENC_A: from pad A (2.5, 7.5) to P1 pad 1 (4.5, 22.5) along X = 0.9 mm corridor
    pa = pads_enc['A']
    p1_1 = pads_p1['1']
    add_track(pa[0], pa[1], 0.9, pa[1], pcbnew.B_Cu, enc_a)
    add_track(0.9, pa[1], 0.9, 19.5, pcbnew.B_Cu, enc_a)
    add_track(0.9, 19.5, p1_1[0], 19.5, pcbnew.B_Cu, enc_a)
    add_track(p1_1[0], 19.5, p1_1[0], p1_1[1], pcbnew.B_Cu, enc_a)

    # Route ENC_B: from pad B (2.5, 12.5) to P1 pad 2 (7.04, 22.5)
    pb = pads_enc['B']
    p1_2 = pads_p1['2']
    add_track(pb[0], pb[1], 3.5, pb[1], pcbnew.B_Cu, enc_b)
    add_track(3.5, pb[1], 3.5, 18.0, pcbnew.B_Cu, enc_b)
    add_track(3.5, 18.0, p1_2[0], 18.0, pcbnew.B_Cu, enc_b)
    add_track(p1_2[0], 18.0, p1_2[0], p1_2[1], pcbnew.B_Cu, enc_b)

    # Route ENC_SW: from pad S1 (17.0, 12.5) to P1 pad 4 (12.12, 22.5)
    psw = pads_enc['S1']
    p1_4 = pads_p1['4']
    add_track(psw[0], psw[1], 18.8, psw[1], pcbnew.B_Cu, enc_sw)
    add_track(18.8, psw[1], 18.8, 19.5, pcbnew.B_Cu, enc_sw)
    add_track(18.8, 19.5, p1_4[0], 19.5, pcbnew.B_Cu, enc_sw)
    add_track(p1_4[0], 19.5, p1_4[0], p1_4[1], pcbnew.B_Cu, enc_sw)

    # Ground planes on F.Cu and B.Cu
    for layer in [pcbnew.F_Cu, pcbnew.B_Cu]:
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer)
        zone.SetNet(gnd)
        outline = zone.Outline()
        outline.NewOutline()
        outline.Append(mm(0.35), mm(0.35))
        outline.Append(mm(W - 0.35), mm(0.35))
        outline.Append(mm(W - 0.35), mm(H - 0.35))
        outline.Append(mm(0.35), mm(H - 0.35))
        zone.SetMinThickness(mm(0.20))
        zone.SetThermalReliefGap(mm(0.25))
        zone.SetThermalReliefSpokeWidth(mm(0.25))
        board.Add(zone)
        
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    
    out_path = 'build/icio500/encoder_board.kicad_pcb'
    board.Save(out_path)
    print(f"Saved {out_path} successfully!")

if __name__ == '__main__':
    build_encoder_board()
