import sys
import pcbnew

def route_missing(board_path):
    board = pcbnew.LoadBoard(board_path)
    
    # We need to connect C26 Pad 2 (gnd) to the nearest gnd track/via
    # And R3 Pad 1 (audio_out) to U2 Pad 7 (audio_out)
    
    # Find C26
    c26 = board.FindFootprintByReference("C26")
    u2 = board.FindFootprintByReference("U2")
    r3 = board.FindFootprintByReference("R3")
    
    if c26:
        pad_gnd = c26.FindPadByNumber("2")
        if pad_gnd:
            # We'll drop a via at the pad to connect to the bottom ground plane (if it exists)
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(pad_gnd.GetPosition())
            via.SetWidth(pcbnew.FromMM(0.8))
            via.SetDrill(pcbnew.FromMM(0.4))
            via.SetNetCode(pad_gnd.GetNetCode())
            board.Add(via)
            print("Added GND via at C26 Pad 2")
            
    if r3 and u2:
        pad_r3 = r3.FindPadByNumber("1")
        pad_u2 = u2.FindPadByNumber("7")
        if pad_r3 and pad_u2:
            # Draw a track on F.Cu
            track = pcbnew.PCB_TRACK(board)
            track.SetStart(pad_r3.GetPosition())
            track.SetEnd(pad_u2.GetPosition())
            track.SetWidth(pcbnew.FromMM(0.25))
            track.SetLayer(pcbnew.F_Cu)
            track.SetNetCode(pad_r3.GetNetCode())
            board.Add(track)
            print("Added track between R3 Pad 1 and U2 Pad 7")
            
    pcbnew.SaveBoard(board_path, board)
    print("Saved board.")

if __name__ == '__main__':
    route_missing('build/icio500/icio500.kicad_pcb')
