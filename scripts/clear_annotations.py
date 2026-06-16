import pcbnew

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

# Layers to clean annotations from (NOT Edge.Cuts which defines board outline)
KEEP_LAYERS = {pcbnew.Edge_Cuts, pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.F_Mask, pcbnew.B_Mask, pcbnew.F_Paste, pcbnew.B_Paste}

drawings = list(board.GetDrawings()) if hasattr(board.GetDrawings(), '__iter__') else []

# Use the lower-level Items() iterator
to_remove = []
for item in board.GetItems():
    try:
        layer = item.GetLayer()
        if layer not in KEEP_LAYERS:
            type_name = type(item).__name__
            if 'TRACK' not in type_name and 'VIA' not in type_name and 'FOOTPRINT' not in type_name and 'PAD' not in type_name:
                to_remove.append(item)
    except:
        pass

print(f"Found {len(to_remove)} annotation items to remove")
for item in to_remove:
    try:
        board.Remove(item)
    except:
        pass

pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
print("Done.")
