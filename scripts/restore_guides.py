import pcbnew

b_old = pcbnew.LoadBoard('commit_dfb5c8d.kicad_pcb')
b_new = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

# Collect the relevant drawings from the old board
to_add = []
for d in b_old.GetDrawings():
    layer = b_old.GetLayerName(d.GetLayer())
    if layer == 'User.Drawings' or layer == 'Dwgs.User':
        if type(d) is pcbnew.PCB_TEXT:
            if "L" in d.GetText() or "room" in d.GetText():
                to_add.append(d)
        elif type(d) is pcbnew.PCB_DIM_ALIGNED:
            to_add.append(d)
        elif type(d) is pcbnew.PCB_SHAPE:
            # Maybe there are lines drawn for the guide? Let's check if they belong to the bracket.
            to_add.append(d) # Just add all shapes on User.Drawings as well.

for d in to_add:
    new_d = d.Duplicate()
    b_new.Add(new_d)

pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', b_new)
print(f"Restored {len(to_add)} original Dwgs.User guides (L bracket annotations/dimensions/shapes).")
