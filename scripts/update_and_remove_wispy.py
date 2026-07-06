import pcbnew

def main():
    board = pcbnew.LoadBoard('build/icio500/faceplate_front.kicad_pcb')
    
    # Remove WispyArt and old EncoderGraphic
    for fp in list(board.GetFootprints()):
        name = fp.GetFPID().GetLibItemName().c_str()
        if 'WispyArt' in name or 'EncoderGraphic' in name:
            board.RemoveNative(fp)
            print(f"Removed {name}")
            
    # Inject the new EncoderGraphicGeometric footprint
    fp = pcbnew.FootprintLoad('build/icio500/custom.pretty', 'EncoderGraphicGeometric')
    board.Add(fp)
    fp.SetPosition(pcbnew.VECTOR2I(int(19.05 * 1e6), int(24.0 * 1e6)))
    fp.SetLayer(pcbnew.F_Cu)
    print("Injected EncoderGraphicGeometric at X=19.05, Y=24.0")
    
    pcbnew.SaveBoard('build/icio500/faceplate_front.kicad_pcb', board)
    print("Successfully updated board!")

if __name__ == '__main__':
    main()
