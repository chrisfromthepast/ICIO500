import pcbnew

def main():
    board = pcbnew.LoadBoard('build/icio500/faceplate_front.kicad_pcb')
    
    # Remove the existing EncoderGraphic footprint
    for fp in list(board.GetFootprints()):
        if 'EncoderGraphic' in fp.GetFPID().GetLibItemName().c_str():
            board.RemoveNative(fp)
            
    # Inject the new EncoderGraphic footprint
    fp = pcbnew.FootprintLoad('build/icio500/custom.pretty', 'EncoderGraphicGeometric')
    board.Add(fp)
    fp.SetPosition(pcbnew.VECTOR2I(int(19.05 * 1e6), int(24.0 * 1e6)))
    fp.SetLayer(pcbnew.F_Cu)
    
    pcbnew.SaveBoard('build/icio500/faceplate_front.kicad_pcb', board)
    print("Successfully updated encoder graphic!")

if __name__ == '__main__':
    main()
