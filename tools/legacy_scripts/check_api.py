import pcbnew
import sys
board = pcbnew.LoadBoard('build/icio500/panel_satellite.kicad_pcb')
print(dir(board))
