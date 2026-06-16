import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

# Clear old graphics
layers_to_clean = [pcbnew.F_SilkS, pcbnew.Cmts_User, pcbnew.Dwgs_User]
items_to_remove = []
for item in board.GetDrawings():
    if item.GetLayer() in layers_to_clean:
        items_to_remove.append(item)

for item in items_to_remove:
    board.Remove(item)

pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
print("Drawings cleared.")
