import sys
import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
try:
    pcbnew.ExportSpecctraDSN(board, 'build/icio500/board.dsn')
    print("DSN Exported successfully")
except Exception as e:
    print(f"Failed: {e}")
