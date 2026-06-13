import pcbnew

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

# Fix 1: Connect C26 pad2 (gnd) to gnd network
c26_p2 = board.FindFootprintByReference('C26').FindPadByNumber('2')
c25_p2 = board.FindFootprintByReference('C25').FindPadByNumber('2')
if c26_p2 and c25_p2:
    gnd_net = c26_p2.GetNetCode()
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(c26_p2.GetPosition())
    t.SetEnd(c25_p2.GetPosition())
    t.SetWidth(pcbnew.FromMM(0.4))
    t.SetLayer(pcbnew.F_Cu)
    t.SetNetCode(gnd_net)
    board.Add(t)

# Fix 2: Connect R3 pad1 (audio_out) to U2 pad7 (audio_out)
r3_p1 = board.FindFootprintByReference('R3').FindPadByNumber('1')
u2_p7 = board.FindFootprintByReference('U2').FindPadByNumber('7')
if r3_p1 and u2_p7:
    ao_net = r3_p1.GetNetCode()
    # Manhattan route via B.Cu to avoid crossings
    via1 = pcbnew.PCB_VIA(board)
    via1.SetPosition(r3_p1.GetPosition())
    via1.SetWidth(pcbnew.FromMM(0.6))
    via1.SetDrill(pcbnew.FromMM(0.3))
    via1.SetNetCode(ao_net)
    board.Add(via1)
    
    via2 = pcbnew.PCB_VIA(board)
    via2.SetPosition(u2_p7.GetPosition())
    via2.SetWidth(pcbnew.FromMM(0.6))
    via2.SetDrill(pcbnew.FromMM(0.3))
    via2.SetNetCode(ao_net)
    board.Add(via2)
    
    mid_x = u2_p7.GetPosition().x
    mid_y = r3_p1.GetPosition().y
    t1 = pcbnew.PCB_TRACK(board)
    t1.SetStart(r3_p1.GetPosition())
    t1.SetEnd(pcbnew.VECTOR2I(mid_x, mid_y))
    t1.SetWidth(pcbnew.FromMM(0.25))
    t1.SetLayer(pcbnew.B_Cu)
    t1.SetNetCode(ao_net)
    board.Add(t1)
    
    t2 = pcbnew.PCB_TRACK(board)
    t2.SetStart(pcbnew.VECTOR2I(mid_x, mid_y))
    t2.SetEnd(u2_p7.GetPosition())
    t2.SetWidth(pcbnew.FromMM(0.25))
    t2.SetLayer(pcbnew.B_Cu)
    t2.SetNetCode(ao_net)
    board.Add(t2)

pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
print('Fixed 2 unconnected')
