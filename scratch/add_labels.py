import pcbnew

BOARD_IN = 'build/icio500/icio500.kicad_pcb'

def add_silkscreen_text(board, text, x, y, layer=pcbnew.F_SilkS, size=2.0, thickness=0.3):
    txt = pcbnew.PCB_TEXT(board)
    txt.SetText(text)
    txt.SetPosition(pcbnew.VECTOR2I(int(x*1e6), int(y*1e6)))
    txt.SetTextSize(pcbnew.VECTOR2I(int(size*1e6), int(size*1e6)))
    txt.SetTextThickness(int(thickness*1e6))
    txt.SetLayer(layer)
    board.Add(txt)

def main():
    board = pcbnew.LoadBoard(BOARD_IN)
    
    # Input Stage
    add_silkscreen_text(board, "BALANCED INPUT STAGE", 155.0, 100.0)
    
    # Output Stage
    add_silkscreen_text(board, "LINE DRIVER STAGE", 155.0, 80.0)
    
    # Scaling / VCA
    add_silkscreen_text(board, "SCALING & SHIFTING", 160.0, 130.0)

    # Power
    add_silkscreen_text(board, "POWER / REGS", 100.0, 130.0)

    pcbnew.SaveBoard(BOARD_IN, board)
    print("Added silkscreen labels.")

if __name__ == '__main__':
    main()
