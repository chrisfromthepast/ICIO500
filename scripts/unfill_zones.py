import pcbnew

board_path = 'build/icio500/icio500.kicad_pcb'
board = pcbnew.LoadBoard(board_path)

# Unfill all zones to prevent DSN export from crashing Freerouting
for zone in board.Zones():
    zone.UnFill()

pcbnew.SaveBoard(board_path, board)
print("Successfully unfilled all zones.")
