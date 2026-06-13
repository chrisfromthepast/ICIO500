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

def route_unconnected(board):
    connectivity = board.GetConnectivity()
    connectivity.Recalculate()
    unconnected = connectivity.GetUnconnectedEdges()
    
    for edge in unconnected:
        s = edge.GetSourceNode()
        t = edge.GetTargetNode()
        
        sx, sy = s.Pos().x / 1e6, s.Pos().y / 1e6
        ex, ey = t.Pos().x / 1e6, t.Pos().y / 1e6
        
        # Check if they are on the same layer? Usually F.Cu for these surface components.
        # Draw a manhattan path
        mid_x = ex
        mid_y = sy
        
        net_code = s.GetNet()
        
        # We assume F.Cu for these short connections
        add_track(board, (sx, sy), (mid_x, mid_y), pcbnew.F_Cu, net_code)
        add_track(board, (mid_x, mid_y), (ex, ey), pcbnew.F_Cu, net_code)
        print(f"Routed from ({sx}, {sy}) to ({ex}, {ey}) on net {net_code}")

def main():
    board = pcbnew.LoadBoard(BOARD_IN)
    route_unconnected(board)
    pcbnew.SaveBoard(BOARD_IN, board)
    print("Done routing unconnected edges.")

if __name__ == '__main__':
    main()
