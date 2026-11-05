"""Move J_ENC away from the BR2/MH2 screw corner and re-route the three encoder
nets (d14, gpio_enc_b, gpio_enc_sw).

J_ENC pad n sits at Y_carrier = 138.025 - 2.54*(n-1), X = 72.0, and mates 1:1
with P1 on the encoder daughtercard (see scripts/generate_encoder_board.py):
  pad1 = ENC_SW (gpio_enc_sw)   Y 138.025
  pad2 = GND                    Y 135.485
  pad3 = ENC_B  (gpio_enc_b)    Y 132.945
  pad4 = GND                    Y 130.405
  pad5 = ENC_A  (d14)           Y 127.865
"""
import pcbnew

MM = 1e6
def mm(v): return int(round(v * MM))

SRC = 'build/icio500/icio500.kicad_pcb'
b = pcbnew.LoadBoard(SRC)

# --- 1. delete every old track / via on the three encoder nets
for t in list(b.GetTracks()):
    if t.GetNetname() in ('d14', 'gpio_enc_b', 'gpio_enc_sw'):
        b.Delete(t)

# --- 2. move J_ENC (keep 180 deg so the pins still point at the faceplate)
j = b.FindFootprintByReference('J_ENC')
j.SetPosition(pcbnew.VECTOR2I(mm(72.0), mm(138.025)))

# --- 3. net assignment on the connector pads
d14 = b.FindNet('d14')
enc_b = b.FindNet('gpio_enc_b')
enc_sw = b.FindNet('gpio_enc_sw')
gnd = b.FindNet('gnd')
want = {'1': enc_sw, '2': gnd, '3': enc_b, '4': gnd, '5': d14}
for p in j.Pads():
    p.SetNet(want[str(p.GetNumber())])
    print('J_ENC pad', p.GetNumber(), p.GetNetname(), round(p.GetPosition().x / MM, 3), round(p.GetPosition().y / MM, 3))

def add_track(x1, y1, x2, y2, net, width=0.25):
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    t.SetLayer(pcbnew.F_Cu)
    t.SetNet(net)
    t.SetWidth(mm(width))
    b.Add(t)

def poly(points, net):
    for a, c in zip(points[:-1], points[1:]):
        add_track(a[0], a[1], c[0], c[1], net)

# U5 pins: d14 (95, 128.10)  gpio_enc_b (95, 130.64)  gpio_enc_sw (95, 133.18)
# all routing on F.Cu, no vias, no crossings
poly([(95.0, 128.10), (92.0, 128.10), (91.765, 127.865), (72.0, 127.865)], d14)
poly([(95.0, 130.64), (84.0, 130.64), (84.0, 132.945), (72.0, 132.945)], enc_b)
poly([(95.0, 133.18), (88.0, 133.18), (88.0, 138.025), (72.0, 138.025)], enc_sw)

pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(SRC)
print('carrier saved')
