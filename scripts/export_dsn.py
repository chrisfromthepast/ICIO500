import pcbnew
import sys

board_path = 'build/icio500/icio500.kicad_pcb'
dsn_path = 'build/icio500/board.dsn'

board = pcbnew.LoadBoard(board_path)
pcbnew.ExportSpecctraDSN(board, dsn_path)
print("DSN exported to", dsn_path)
