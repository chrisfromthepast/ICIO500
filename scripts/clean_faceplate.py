import pcbnew

def main():
    board = pcbnew.LoadBoard('build/icio500/faceplate_front.kicad_pcb')
    
    # Remove all tracks
    tracks = board.GetTracks()
    for t in tracks:
        board.RemoveNative(t)
        
    # Remove all zones
    zones = board.Zones()
    for z in zones:
        board.RemoveNative(z)
        
    pcbnew.SaveBoard('build/icio500/faceplate_front.kicad_pcb', board)
    print("Cleaned up rogue tracks and zones!")

if __name__ == '__main__':
    main()
