import pcbnew

board_path = 'build/icio500/icio500.kicad_pcb'
board = pcbnew.LoadBoard(board_path)

# Move C26 left by 4mm to avoid R3 and R4
c26 = board.FindFootprintByReference("C26")
if c26:
    pos = c26.GetPosition()
    pos.x -= int(4.0 * 1e6)
    c26.SetPosition(pos)

pcbnew.SaveBoard(board_path, board)
print("Moved C26.")
