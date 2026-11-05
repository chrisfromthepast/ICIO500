import pcbnew
import os

MM = 1e6
def mm(v): return int(round(v * MM))

# ---------------------------------------------------------------------------
# Encoder daughtercard geometry (board coordinates, mm)
#   x = 0   : plane of carrier top surface (x grows away from the carrier)
#   y       : Y_carrier = 135.525 + y   (shaft/dial centre is y = 10.0 -> 145.525)
#
# Würth WP-SMRA-M3 bracket BR2 (screw to the carrier at MH2) occupies, in this
# frame:  X_carrier 54.175..59.5, Y_carrier 152.3..157.7 (y 16.8..22.2),
#         board-x up to +3.75.
# The daughtercard must NEVER touch that volume, so:
#   * the 5-pin connector (P1 / J_ENC) lives on the *upper* part of the card
#     (y < 3), far away from the screw corner,
#   * the lower-left corner of the card is notched away (x < NOTCH_X, y > NOTCH_Y)
#     so the card stays clear of the bracket body and the screw.
# ---------------------------------------------------------------------------
W = 18.0
Y_TOP = -9.0
Y_BOT = 18.4
NOTCH_X = 4.4
NOTCH_Y = 13.2

def build_encoder_board():
    board = pcbnew.BOARD()

    ds = board.GetDesignSettings()
    ds.SetBoardThickness(mm(1.6))
    ds.m_CopperEdgeClearance = mm(0.35)
    ds.m_TrackClearance = mm(0.20)

    # Edge.Cuts: rectangle with a notch in the carrier-side lower corner
    pts = [(0.0, Y_TOP), (W, Y_TOP), (W, Y_BOT), (NOTCH_X, Y_BOT),
           (NOTCH_X, NOTCH_Y), (0.0, NOTCH_Y)]
    for i in range(len(pts)):
        p1 = pts[i]
        p2 = pts[(i + 1) % len(pts)]
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

    # ENC1: shaft centre at (8.5, 10.0).  Rot 270 puts every pad at x >= 2.9.
    enc_fp = pcbnew.FootprintLoad(enc_lib, 'RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm')
    enc_fp.SetReference('ENC1')
    enc_fp.SetValue('PEC11R-4020F-S0024')
    enc_fp.SetOrientation(pcbnew.EDA_ANGLE(270, pcbnew.DEGREES_T))
    enc_fp.SetPosition(pcbnew.VECTOR2I(mm(11.0), mm(2.5)))

    step_path = os.path.abspath('build/icio500/RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm.step')
    if enc_fp.Models() and os.path.exists(step_path):
        m = enc_fp.Models()[0]
        m.m_Filename = step_path
        m.m_Rotation = pcbnew.VECTOR3D(0, 0, 270)
        m.m_Offset = pcbnew.VECTOR3D(7.5, 2.5, 0.0)

    for it in list(enc_fp.GraphicalItems()):
        enc_fp.Delete(it)
    enc_fp.Reference().SetVisible(False)
    enc_fp.Value().SetVisible(False)
    board.Add(enc_fp)

    for pad in enc_fp.Pads():
        num = str(pad.GetNumber())
        if num == 'A':
            pad.SetNet(enc_a)
        elif num == 'B':
            pad.SetNet(enc_b)
        elif num in ('C', 'S2') or 'MP' in num:
            pad.SetNet(gnd)
        elif num == 'S1':
            pad.SetNet(enc_sw)

    # P1: 1x5 female socket on the REAR (B.Cu), rotated 180, x = 2.3.
    # Pad 1 at y = 2.5 (Y_carrier 138.025) ... pad 5 at y = -7.66 (127.865).
    # Mates 1:1 with J_ENC on the carrier (same pad number = same Y_carrier).
    p1_fp = pcbnew.FootprintLoad(hdr_lib, 'PinSocket_1x05_P2.54mm_Vertical')
    p1_fp.SetReference('P1')
    p1_fp.SetValue('Conn_01x05_Female')
    board.Add(p1_fp)
    p1_fp.SetOrientation(pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))
    p1_fp.Flip(pcbnew.VECTOR2I(0, 0), False)
    p1_fp.SetPosition(pcbnew.VECTOR2I(mm(2.3), mm(2.5)))

    for it in list(p1_fp.GraphicalItems()):
        p1_fp.Delete(it)
    p1_fp.Reference().SetVisible(False)
    p1_fp.Value().SetVisible(False)

    # pin 1 = ENC_SW, 2 = GND, 3 = ENC_B, 4 = GND, 5 = ENC_A
    p1_map = {'1': enc_sw, '2': gnd, '3': enc_b, '4': gnd, '5': enc_a}
    for pad in p1_fp.Pads():
        num = str(pad.GetNumber())
        if num in p1_map:
            pad.SetNet(p1_map[num])

    pads_enc = {}
    for p in enc_fp.Pads():
        pads_enc[str(p.GetNumber())] = (p.GetPosition().x / MM, p.GetPosition().y / MM)
    pads_p1 = {str(p.GetNumber()): (p.GetPosition().x / MM, p.GetPosition().y / MM) for p in p1_fp.Pads()}

    def add_track(x1, y1, x2, y2, layer, net, width=0.25):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
        t.SetLayer(layer)
        t.SetNet(net)
        t.SetWidth(mm(width))
        board.Add(t)

    def poly(points, layer, net):
        for (a, b) in zip(points[:-1], points[1:]):
            add_track(a[0], a[1], b[0], b[1], layer, net)

    # ENC_A: pad A (11, 2.5) -> north -> west along y = P1 pin 5
    pa = pads_enc['A']; p5 = pads_p1['5']
    poly([pa, (pa[0], p5[1]), p5], pcbnew.F_Cu, enc_a)

    # ENC_B: pad B (6, 2.5) -> north -> west to P1 pin 3
    pb = pads_enc['B']; p3 = pads_p1['3']
    poly([pb, (pb[0], p3[1]), p3], pcbnew.F_Cu, enc_b)

    # ENC_SW: pad S1 (6, 17) -> up the middle of the card -> P1 pin 1
    ps = pads_enc['S1']; p1 = pads_p1['1']
    poly([ps, (5.4, ps[1] - 0.6), (5.4, 10.9), (5.0, 6.0), (3.2, 4.5), p1], pcbnew.F_Cu, enc_sw)

    # Ground pours on both layers, solid-connected to every GND pad
    zone_pts = [(0.35, Y_TOP + 0.35), (W - 0.35, Y_TOP + 0.35), (W - 0.35, Y_BOT - 0.35),
                (NOTCH_X + 0.35, Y_BOT - 0.35), (NOTCH_X + 0.35, NOTCH_Y - 0.35), (0.35, NOTCH_Y - 0.35)]
    for layer in [pcbnew.F_Cu, pcbnew.B_Cu]:
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer)
        zone.SetNet(gnd)
        outline = zone.Outline()
        outline.NewOutline()
        for (x, y) in zone_pts:
            outline.Append(mm(x), mm(y))
        zone.SetMinThickness(mm(0.20))
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        board.Add(zone)

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())

    out_path = 'build/icio500/encoder_board.kicad_pcb'
    board.Save(out_path)
    print(f"Saved {out_path} successfully!")
    for k, v in sorted(pads_enc.items()):
        print('  ENC pad', k, v)
    for k, v in sorted(pads_p1.items()):
        print('  P1  pad', k, v, '-> Y_carrier %.3f' % (135.525 + v[1]))

if __name__ == '__main__':
    build_encoder_board()
