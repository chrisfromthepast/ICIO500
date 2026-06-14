import pcbnew
import os

def mm(v): return int(v * 1_000_000)

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

gnd_net = board.FindNet('GND_Audio')
v5_net = board.FindNet('V_Plus_5V')
vin_net = board.FindNet('V_Plus_Analog')

# Find footprints
u1 = board.FindFootprintByReference('U1')
c5 = board.FindFootprintByReference('C5')
c6 = board.FindFootprintByReference('C6')

if u1:
    # U1 is a TO-220-3_Vertical footprint.
    # We will place it near the top left corner (where the old U1 was, but take up much less space)
    # Old U1 was around X=142, Y=105
    u1.SetPosition(pcbnew.VECTOR2I(mm(142), mm(100)))
    u1.SetOrientationDegrees(90)
    
if c5:
    c5.SetPosition(pcbnew.VECTOR2I(mm(146), mm(98)))
    c5.SetOrientationDegrees(90)
    for pad in c5.Pads():
        if pad.GetName() == '1': pad.SetNet(v5_net)
        if pad.GetName() == '2': pad.SetNet(gnd_net)
        
if c6:
    c6.SetPosition(pcbnew.VECTOR2I(mm(146), mm(102)))
    c6.SetOrientationDegrees(90)
    for pad in c6.Pads():
        if pad.GetName() == '1': pad.SetNet(v5_net)
        if pad.GetName() == '2': pad.SetNet(gnd_net)

board.Save('build/icio500/icio500.kicad_pcb')
print("Power components updated and placed.")
