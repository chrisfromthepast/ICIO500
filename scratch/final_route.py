import pcbnew

def add_track(board, start, end, layer, net, width=0.25):
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(pcbnew.VECTOR2I(int(start[0]*1e6), int(start[1]*1e6)))
    track.SetEnd(pcbnew.VECTOR2I(int(end[0]*1e6), int(end[1]*1e6)))
    track.SetWidth(pcbnew.FromMM(width))
    track.SetLayer(layer)
    track.SetNetCode(net)
    board.Add(track)
    return track

def add_via(board, pos, net):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I(int(pos[0]*1e6), int(pos[1]*1e6)))
    via.SetWidth(pcbnew.FromMM(0.6))
    via.SetDrill(pcbnew.FromMM(0.3))
    via.SetNetCode(net)
    board.Add(via)
    return via

def main():
    board_path = 'build/icio500/icio500.kicad_pcb'
    board = pcbnew.LoadBoard(board_path)
    
    # GND fix
    c26 = board.FindFootprintByReference("C26")
    c26_p2 = c26.FindPadByNumber("2")
    net_gnd = c26_p2.GetNetCode()
    c26_p2_pos = (c26_p2.GetPosition().x/1e6, c26_p2.GetPosition().y/1e6)
    add_via(board, c26_p2_pos, net_gnd)
    
    add_via(board, (174.3026, 92.2250), net_gnd)
    
    # R3 pad 1 to U2 pad 7
    r3 = board.FindFootprintByReference("R3")
    u2 = board.FindFootprintByReference("U2")
    r3_p1 = r3.FindPadByNumber("1")
    u2_p7 = u2.FindPadByNumber("7")
    net_audio = r3_p1.GetNetCode()
    
    r3_p1_pos = (r3_p1.GetPosition().x/1e6, r3_p1.GetPosition().y/1e6)
    u2_p7_pos = (u2_p7.GetPosition().x/1e6, u2_p7.GetPosition().y/1e6)
    
    v1 = (r3_p1_pos[0], r3_p1_pos[1] - 1.5)
    v2 = (u2_p7_pos[0] + 1.2, u2_p7_pos[1])
    
    add_track(board, r3_p1_pos, v1, pcbnew.F_Cu, net_audio)
    add_via(board, v1, net_audio)
    
    add_track(board, u2_p7_pos, v2, pcbnew.F_Cu, net_audio)
    add_via(board, v2, net_audio)
    
    pts_audio = [v1, (164.5, v1[1]), (164.5, v2[1]), v2]
    for i in range(len(pts_audio)-1):
        add_track(board, pts_audio[i], pts_audio[i+1], pcbnew.B_Cu, net_audio)
        
    # C26 pad 1 to R8 pad 2
    c26_p1 = c26.FindPadByNumber("1")
    r8 = board.FindFootprintByReference("R8")
    r8_p2 = r8.FindPadByNumber("2")
    net_zobel = c26_p1.GetNetCode()
    
    c26_p1_pos = (c26_p1.GetPosition().x/1e6, c26_p1.GetPosition().y/1e6)
    r8_p2_pos = (r8_p2.GetPosition().x/1e6, r8_p2.GetPosition().y/1e6)
    
    v3 = (c26_p1_pos[0], c26_p1_pos[1] - 1.5)
    v4 = (r8_p2_pos[0] + 1.2, r8_p2_pos[1])
    
    add_track(board, c26_p1_pos, v3, pcbnew.F_Cu, net_zobel)
    add_via(board, v3, net_zobel)
    
    add_track(board, r8_p2_pos, v4, pcbnew.F_Cu, net_zobel)
    add_via(board, v4, net_zobel)
    
    pts_zobel = [v3, (168.0, v3[1]), (168.0, v4[1]), v4]
    for i in range(len(pts_zobel)-1):
        add_track(board, pts_zobel[i], pts_zobel[i+1], pcbnew.B_Cu, net_zobel)

    pcbnew.SaveBoard(board_path, board)
    print("Saved final route.")

if __name__ == '__main__':
    main()
