import pcbnew

def main():
    new_board = pcbnew.LoadBoard('build/icio500/faceplate_front.kicad_pcb')
    
    # Remove all text (silkscreen or otherwise) from the faceplate front board
    for dwg in list(new_board.GetDrawings()):
        if isinstance(dwg, pcbnew.PCB_TEXT):
            new_board.RemoveNative(dwg)
            
    pcbnew.SaveBoard('build/icio500/faceplate_front.kicad_pcb', new_board)
    print("Successfully removed all text!")

if __name__ == "__main__":
    main()
