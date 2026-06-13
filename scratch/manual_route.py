import pcbnew

def main():
    board_path = 'build/icio500/icio500.kicad_pcb'
    board = pcbnew.LoadBoard(board_path)
    
    def add_track(start, end, layer, net, width=0.25):
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(pcbnew.VECTOR2I(int(start[0]*1e6), int(start[1]*1e6)))
        track.SetEnd(pcbnew.VECTOR2I(int(end[0]*1e6), int(end[1]*1e6)))
        track.SetWidth(pcbnew.FromMM(width))
        track.SetLayer(layer)
        track.SetNetCode(net)
        board.Add(track)

    def add_via(pos, net):
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(pcbnew.VECTOR2I(int(pos[0]*1e6), int(pos[1]*1e6)))
        via.SetWidth(pcbnew.FromMM(0.6))
        via.SetDrill(pcbnew.FromMM(0.3))
        via.SetNetCode(net)
        board.Add(via)

    # 1. Audio Path (R3 Pad 1 -> U2 Pad 7)
    r3 = board.FindFootprintByReference("R3")
    u2 = board.FindFootprintByReference("U2")
    r3_p1 = r3.FindPadByNumber("1")
    u2_p7 = u2.FindPadByNumber("7")
    net_audio = r3_p1.GetNetCode()
    
    r3_pos = (r3_p1.GetPosition().x/1e6, r3_p1.GetPosition().y/1e6)
    u2_pos = (u2_p7.GetPosition().x/1e6, u2_p7.GetPosition().y/1e6)
    
    via1_pos = (r3_pos[0], r3_pos[1] - 1.5) # UP 1.5mm to avoid horizontal density
    via2_pos = (u2_pos[0] + 1.2, u2_pos[1]) # RIGHT 1.2mm (safe from previous tests)
    
    add_track(r3_pos, via1_pos, pcbnew.F_Cu, net_audio)
    add_track(u2_pos, via2_pos, pcbnew.F_Cu, net_audio)
    
    add_via(via1_pos, net_audio)
    add_via(via2_pos, net_audio)
    
    pts_audio = [
        via1_pos,
        (164.5, via1_pos[1]),
        (164.5, via2_pos[1]),
        via2_pos
    ]
    for i in range(len(pts_audio)-1):
        add_track(pts_audio[i], pts_audio[i+1], pcbnew.B_Cu, net_audio)
        
    # 2. GND Path (C26 Pad 2 -> GND Track)
    c26 = board.FindFootprintByReference("C26")
    c26_p2 = c26.FindPadByNumber("2")
    net_gnd = c26_p2.GetNetCode()
    
    c26_pos = (c26_p2.GetPosition().x/1e6, c26_p2.GetPosition().y/1e6)
    via3_pos = (c26_pos[0], c26_pos[1] - 1.5) # UP 1.5mm to avoid horizontal density
    via4_pos = (170.0, 92.225)
    
    add_track(c26_pos, via3_pos, pcbnew.F_Cu, net_gnd)
    
    add_via(via3_pos, net_gnd)
    add_via(via4_pos, net_gnd)
    
    pts_gnd = [
        via3_pos,
        (161.0, via3_pos[1]),
        (161.0, via4_pos[1]),
        via4_pos
    ]
    for i in range(len(pts_gnd)-1):
        add_track(pts_gnd[i], pts_gnd[i+1], pcbnew.B_Cu, net_gnd)

    pcbnew.SaveBoard(board_path, board)
    print("Saved manual route with vertical offsets.")

if __name__ == '__main__':
    main()
