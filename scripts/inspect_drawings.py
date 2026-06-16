import pcbnew
old_b = pcbnew.LoadBoard('old_board.kicad_pcb')
for d in old_b.GetDrawings():
    layer_name = old_b.GetLayerName(d.GetLayer())
    if type(d) is pcbnew.PCB_TEXT:
        print(f"TEXT [{layer_name}]: {d.GetText()}")
    elif type(d) is pcbnew.PCB_DIM_ALIGNED:
        print(f"DIMENSION [{layer_name}]")
    else:
        print(f"SHAPE [{layer_name}]")
