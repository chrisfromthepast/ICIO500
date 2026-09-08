import pcbnew
import sys
try:
    board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
    print("Board loaded successfully. Tracks:", len(board.GetTracks()))
except Exception as e:
    print("Error loading board:", e)
