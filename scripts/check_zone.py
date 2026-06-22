import pcbnew
board_path = 'build/icio500/icio500.kicad_pcb'
board = pcbnew.LoadBoard(board_path)
rule_area = pcbnew.ZONE(board)
print([a for a in dir(rule_area) if 'Allow' in a or 'Keep' in a])
