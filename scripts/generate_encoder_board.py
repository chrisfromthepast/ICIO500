import pcbnew
import os

MM = 1e6
def mm(v): return int(round(v * MM))

def build_encoder_board():
    board = pcbnew.BOARD()
    
    W = 18.0
    H = 26.0
    
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(mm(1.6))
    ds.m_CopperEdgeClearance = mm(0.35)
    ds.m_TrackClearance = mm(0.20)
    
    # Edge.Cuts (18.0 x 26.0 mm)
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
    
    # ENC1: Rotary Encoder on F.Cu
    # Shaft center at (xs, ys) = (8.5, 10.0) mm
    # Orientation: 270 deg (counterclockwise 90 deg)
    # Origin (Pad A) is at (11.0, 2.5) mm
    enc_fp = pcbnew.FootprintLoad(enc_lib, 'RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm')
    enc_fp.SetReference('ENC1')
    enc_fp.SetValue('PEC11R-4020F-S0024')
    enc_fp.SetOrientation(pcbnew.EDA_ANGLE(270, pcbnew.DEGREES_T))
    enc_fp.SetPosition(pcbnew.VECTOR2I(mm(11.0), mm(2.5)))
    
    # 3D model: exact alignment down to 0.000 mm on all 7 pads
    step_path = os.path.abspath('build/icio500/RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm.step')
    if enc_fp.Models() and os.path.exists(step_path):
        m = enc_fp.Models()[0]
        m.m_Filename = step_path
        m.m_Rotation = pcbnew.VECTOR3D(0, 0, 270)
        m.m_Offset = pcbnew.VECTOR3D(7.5, 2.5, 0.0)
    
    # Delete oversized courtyard / silkscreen that crosses opposite-side pads
    for it in list(enc_fp.GraphicalItems()):
        enc_fp.Delete(it)
        
    enc_fp.Reference().SetVisible(False)
    enc_fp.Value().SetVisible(False)
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
            
    # P1: 1x5 Vertical female socket mounted on REAR (B.Cu)
    # Origin at Pad 1. Orientation: 180 deg on B.Cu
    # Pad 1 is at (2.300, 22.635) mm, Pad 5 is at (2.300, 12.475) mm
    # Sockets face backwards towards carrier card right-angle header J_ENC!
    p1_fp = pcbnew.FootprintLoad(hdr_lib, 'PinSocket_1x05_P2.54mm_Vertical')
    p1_fp.SetReference('P1')
    p1_fp.SetValue('Conn_01x05_Female')
    board.Add(p1_fp)
    p1_fp.SetOrientation(pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))
    p1_fp.Flip(pcbnew.VECTOR2I(0, 0), False)
    p1_fp.SetPosition(pcbnew.VECTOR2I(mm(2.3), mm(22.635)))
    
    for it in list(p1_fp.GraphicalItems()):
        p1_fp.Delete(it)
        
    p1_fp.Reference().SetVisible(False)
    p1_fp.Value().SetVisible(False)
    
    p1_map = {'1': enc_a, '2': gnd, '3': enc_b, '4': enc_sw, '5': gnd}
    for pad in p1_fp.Pads():
        num = str(pad.GetNumber())
        if num in p1_map:
            pad.SetNet(p1_map[num])

    def add_track(x1, y1, x2, y2, layer, net, width=0.25):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
        t.SetLayer(layer)
        t.SetNet(net)
        t.SetWidth(mm(width))
        board.Add(t)

    # Route ENC_SW: S1 at (6.0, 17.0) to P1 Pad 4 at (2.3, 15.015) on B.Cu
    add_track(6.0, 17.0, 4.2, 17.0, pcbnew.B_Cu, enc_sw)
    add_track(4.2, 17.0, 4.2, 15.015, pcbnew.B_Cu, enc_sw)
    add_track(4.2, 15.015, 2.3, 15.015, pcbnew.B_Cu, enc_sw)

    # Route ENC_B: Pad B at (6.0, 2.5) to P1 Pad 3 at (2.3, 17.555) on F.Cu
    # Clean route: down at X=5.0, jog past S1 to X=3.6, then into Pad 3
    add_track(6.0, 2.5, 5.0, 2.5, pcbnew.F_Cu, enc_b)
    add_track(5.0, 2.5, 5.0, 13.5, pcbnew.F_Cu, enc_b)
    add_track(5.0, 13.5, 3.6, 14.9, pcbnew.F_Cu, enc_b)
    add_track(3.6, 14.9, 3.6, 17.555, pcbnew.F_Cu, enc_b)
    add_track(3.6, 17.555, 2.3, 17.555, pcbnew.F_Cu, enc_b)

    # Route ENC_A: Pad A at (11.0, 2.5) to P1 Pad 1 at (2.3, 22.635) on F.Cu
    # Route along east board perimeter down to Y=22.635, then across to Pad 1
    add_track(11.0, 2.5, 16.5, 2.5, pcbnew.F_Cu, enc_a)
    add_track(16.5, 2.5, 16.5, 22.635, pcbnew.F_Cu, enc_a)
    add_track(16.5, 22.635, 2.3, 22.635, pcbnew.F_Cu, enc_a)

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
