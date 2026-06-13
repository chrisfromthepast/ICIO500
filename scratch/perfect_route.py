import pcbnew
import shutil

BOARD_IN = 'build/icio500/icio500.kicad_pcb'

def add_track(board, start, end, layer, net, width=0.25):
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(pcbnew.VECTOR2I(int(start[0]*1e6), int(start[1]*1e6)))
    track.SetEnd(pcbnew.VECTOR2I(int(end[0]*1e6), int(end[1]*1e6)))
    track.SetWidth(pcbnew.FromMM(width))
    track.SetLayer(layer)
    track.SetNetCode(net)
    board.Add(track)

def add_via(board, pos, net):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I(int(pos[0]*1e6), int(pos[1]*1e6)))
    via.SetWidth(pcbnew.FromMM(0.6))
    via.SetDrill(pcbnew.FromMM(0.3))
    via.SetNetCode(net)
    board.Add(via)

def main():
    board = pcbnew.LoadBoard(BOARD_IN)
    
    # 1. GND
    c26 = board.FindFootprintByReference("C26")
    c26_p2 = c26.FindPadByNumber("2")
    net_gnd = c26_p2.GetNetCode()
    
    # C26 is at 153.0. Pad 2 is at ~153.0, 86.225
    c26_p2_pos = (c26_p2.GetPosition().x/1e6, c26_p2.GetPosition().y/1e6)
    add_via(board, c26_p2_pos, net_gnd)
    
    add_via(board, (174.3026, 92.2250), net_gnd)
    
    # Fill zones to connect GND vias to the internal B.Cu ground plane
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    
    # 2. Audio Out
    r3 = board.FindFootprintByReference("R3")
    u2 = board.FindFootprintByReference("U2")
    r3_p1 = r3.FindPadByNumber("1")
    u2_p7 = u2.FindPadByNumber("7")
    net_audio = r3_p1.GetNetCode()
    
    r3_pos = (r3_p1.GetPosition().x/1e6, r3_p1.GetPosition().y/1e6)
    u2_pos = (u2_p7.GetPosition().x/1e6, u2_p7.GetPosition().y/1e6)
    
    audio_y = 84.0
    v1 = (r3_pos[0], audio_y)
    v2 = (u2_pos[0] + 1.2, u2_pos[1])
    
    add_track(board, r3_pos, v1, pcbnew.F_Cu, net_audio)
    add_via(board, v1, net_audio)
    add_track(board, u2_pos, v2, pcbnew.F_Cu, net_audio)
    add_via(board, v2, net_audio)
    pts1 = [v1, (164.5, v1[1]), (164.5, v2[1]), v2]
    for i in range(3): add_track(board, pts1[i], pts1[i+1], pcbnew.B_Cu, net_audio)

    # 3. Zobel
    c26_p1 = c26.FindPadByNumber("1")
    r8 = board.FindFootprintByReference("R8")
    r8_p2 = r8.FindPadByNumber("2")
    net_zobel = c26_p1.GetNetCode()
    
    c26_pos = (c26_p1.GetPosition().x/1e6, c26_p1.GetPosition().y/1e6)
    r8_pos = (r8_p2.GetPosition().x/1e6, r8_p2.GetPosition().y/1e6)
    
    zobel_y = 84.5
    v3 = (c26_pos[0], zobel_y)
    v4 = (r8_pos[0] + 1.2, r8_pos[1])
    
    add_track(board, c26_pos, v3, pcbnew.F_Cu, net_zobel)
    add_via(board, v3, net_zobel)
    add_track(board, r8_pos, v4, pcbnew.F_Cu, net_zobel)
    add_via(board, v4, net_zobel)
    pts2 = [v3, (168.0, v3[1]), (168.0, v4[1]), v4]
    for i in range(3): add_track(board, pts2[i], pts2[i+1], pcbnew.B_Cu, net_zobel)
    
    pcbnew.SaveBoard(BOARD_IN, board)
    print("Perfect route applied!")

if __name__ == '__main__':
    main()
