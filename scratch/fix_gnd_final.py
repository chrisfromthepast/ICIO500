import pcbnew
import math

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
    
    # Target 1: C26 pad 2 to Track [gnd] at (154.7122 mm, 71.9050 mm)
    c26 = board.FindFootprintByReference("C26")
    c26_p2 = c26.FindPadByNumber("2")
    net_gnd = c26_p2.GetNetCode()
    
    p1 = (c26_p2.GetPosition().x/1e6, c26_p2.GetPosition().y/1e6)
    t1 = (154.7122, 71.9050)
    
    # Route on B.Cu using a simple Manhattan path
    # drop via at C26 pad 2
    add_via(board, p1, net_gnd)
    
    v1 = (p1[0], t1[1])
    add_track(board, p1, v1, pcbnew.B_Cu, net_gnd)
    add_track(board, v1, t1, pcbnew.B_Cu, net_gnd)
    
    # Target 2: dangling track at (174.3026 mm, 92.2250 mm) to Pad 2 [gnd] of C25 at (170.0000 mm, 92.2250 mm)
    p2 = (174.3026, 92.2250)
    t2 = (170.0000, 92.2250)
    
    # Track on F.Cu directly (since C25 is likely on F.Cu and the track is on F.Cu)
    add_track(board, p2, t2, pcbnew.F_Cu, net_gnd)
    
    pcbnew.SaveBoard(BOARD_IN, board)
    print("Final explicit GND routing applied.")

if __name__ == '__main__':
    main()
