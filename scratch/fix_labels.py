import pcbnew

BOARD_IN = 'build/icio500/icio500.kicad_pcb'

def main():
    board = pcbnew.LoadBoard(BOARD_IN)
    
    # Remove old text on F.Silkscreen that I added
    to_remove = []
    for dwg in board.GetDrawings():
        if isinstance(dwg, pcbnew.PCB_TEXT) and dwg.GetLayer() == pcbnew.F_SilkS:
            text = dwg.GetText()
            if text in ["BALANCED INPUT STAGE", "LINE DRIVER STAGE", "SCALING & SHIFTING", "POWER / REGS"]:
                to_remove.append(dwg)
                
    for dwg in to_remove:
        board.Remove(dwg)
        
    def add_silkscreen_text(text, x, y, size=1.5, thickness=0.3):
        txt = pcbnew.PCB_TEXT(board)
        txt.SetText(text)
        txt.SetPosition(pcbnew.VECTOR2I(int(x*1e6), int(y*1e6)))
        txt.SetTextSize(pcbnew.VECTOR2I(int(size*1e6), int(size*1e6)))
        txt.SetTextThickness(int(thickness*1e6))
        txt.SetLayer(pcbnew.F_SilkS)
        board.Add(txt)

    # Correct locations
    # Line Driver (U1) is around Y=65
    add_silkscreen_text("LINE DRIVER STAGE", 145.0, 65.0)
    
    # Scaling & Shifting (U3) is around Y=90
    add_silkscreen_text("SCALING & SHIFTING", 145.0, 90.0)
    
    # Balanced Input Stage (U2) is around Y=105
    add_silkscreen_text("BALANCED INPUT STAGE", 145.0, 105.0)
    
    # Power / Regs (C1, C3, D1, D2) is around Y=132
    add_silkscreen_text("POWER CONDITIONING", 145.0, 135.0)

    pcbnew.SaveBoard(BOARD_IN, board)
    print("Fixed silkscreen labels.")

if __name__ == '__main__':
    main()
