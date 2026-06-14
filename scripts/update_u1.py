import pcbnew
import os

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

u1 = board.FindFootprintByReference('U1')
if u1:
    print("Found U1, changing footprint...")
    u1.SetFPID(pcbnew.LIB_ID('Package_TO_SOT_THT', 'TO-220-3_Vertical'))
    
    # Let's get the nets we need to assign
    vin_net = board.FindNet('V_Plus_Analog')
    if not vin_net:
        vin_net = pcbnew.NETINFO_ITEM(board, 'V_Plus_Analog')
        board.Add(vin_net)
        
    gnd_net = board.FindNet('GND_Audio')
    if not gnd_net:
        gnd_net = pcbnew.NETINFO_ITEM(board, 'GND_Audio')
        board.Add(gnd_net)
        
    vout_net = board.FindNet('V_Plus_5V')
    if not vout_net:
        vout_net = pcbnew.NETINFO_ITEM(board, 'V_Plus_5V')
        board.Add(vout_net)

    for pad in u1.Pads():
        if pad.GetName() == '1':
            pad.SetNet(vin_net)
        elif pad.GetName() == '2':
            pad.SetNet(gnd_net)
        elif pad.GetName() == '3':
            pad.SetNet(vout_net)
            
    # Also delete C_iso_bulk and C_iso_cer if they are still on the board but disconnected
    # (actually they are replaced by C5 and C6 which are already on the board but need their nets updated)
    
    print("U1 updated.")

board.Save('build/icio500/icio500.kicad_pcb')
print("Board saved.")
