import pcbnew

b_old = pcbnew.LoadBoard('commit_dfb5c8d.kicad_pcb')
b = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

# 1. Strip all current Dwgs.User and F.Silkscreen texts and shapes
to_remove = []
for d in b.GetDrawings():
    layer = b.GetLayerName(d.GetLayer())
    if layer in ['Dwgs.User', 'F.Silkscreen']:
        if type(d) in [pcbnew.PCB_TEXT, pcbnew.PCB_SHAPE]:
            to_remove.append(d)
            
for d in to_remove:
    b.Remove(d)

# 2. Copy F.Silkscreen shapes and texts from old board
for d in b_old.GetDrawings():
    layer = b_old.GetLayerName(d.GetLayer())
    if layer == 'F.Silkscreen':
        if type(d) in [pcbnew.PCB_TEXT, pcbnew.PCB_SHAPE]:
            b.Add(d.Duplicate())

# 3. Define the component groups
groups = {
    'LINE DRIVER': ['U4', 'C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26', 'R7', 'R8'],
    'SCALING': ['U3', 'C15', 'C16', 'C17', 'C18', 'R3', 'R4', 'R5', 'R6'],
    'BALANCED INPUT': ['U2', 'C7', 'C8', 'C13', 'C14', 'R1', 'R2', 'D3', 'D4', 'D5', 'D6'],
    'POWER': ['U1', 'C1', 'C2', 'C3', 'C4', 'C9', 'C10', 'C11', 'C12'],
    'DIGITAL PROCESSING': ['U5', 'U6', 'U7', 'C5', 'C6']
}

# 4. Define the translations for each group
translations = {
    'DIGITAL PROCESSING': pcbnew.VECTOR2I(int(44 * 1e6), int(-9 * 1e6)),
    'POWER': pcbnew.VECTOR2I(int(-1 * 1e6), int(-16 * 1e6)),
    'LINE DRIVER': pcbnew.VECTOR2I(int(-5 * 1e6), int(0)),
    'BALANCED INPUT': pcbnew.VECTOR2I(int(5.5 * 1e6), int(0)),
    'SCALING': pcbnew.VECTOR2I(int(15 * 1e6), int(53.5 * 1e6))
}

# 5. Apply translations to components
for name, refs in groups.items():
    delta = translations[name]
    for ref in refs:
        fp = b.FindFootprintByReference(ref)
        if fp:
            pos = fp.GetPosition()
            fp.SetPosition(pcbnew.VECTOR2I(pos.x + delta.x, pos.y + delta.y))

# 6. Explicitly place D1 and D2 on the right edge, clear of silkscreen boxes
# Edge is at X=195. J1 is at 198.5. SCALING box ends at X=185.
fp_d1 = b.FindFootprintByReference('D1')
if fp_d1:
    fp_d1.SetPosition(pcbnew.VECTOR2I(int(190 * 1e6), int(135 * 1e6)))

fp_d2 = b.FindFootprintByReference('D2')
if fp_d2:
    fp_d2.SetPosition(pcbnew.VECTOR2I(int(190 * 1e6), int(145 * 1e6)))

b.BuildConnectivity()
pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', b)
print("Restored original silkscreen and moved parts into their professional boxes.")
