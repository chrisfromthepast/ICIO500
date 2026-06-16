import pcbnew
b = pcbnew.LoadBoard('commit_dfb5c8d.kicad_pcb')

groups = {
    'LINE DRIVER': ['U4', 'C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26', 'R7', 'R8'],
    'SCALING': ['U3', 'C15', 'C16', 'C17', 'C18', 'R3', 'R4', 'R5', 'R6'],
    'BALANCED INPUT': ['U2', 'C7', 'C8', 'C13', 'C14', 'R1', 'R2', 'D3', 'D4', 'D5', 'D6'],
    'POWER': ['U1', 'C1', 'C2', 'C3', 'C4', 'C9', 'C10', 'C11', 'C12'],
}

for name, refs in groups.items():
    min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
    for ref in refs:
        fp = b.FindFootprintByReference(ref)
        if fp:
            bb = fp.GetBoundingBox()
            min_x = min(min_x, bb.GetLeft() / 1e6)
            max_x = max(max_x, bb.GetRight() / 1e6)
            min_y = min(min_y, bb.GetTop() / 1e6)
            max_y = max(max_y, bb.GetBottom() / 1e6)
    width = max_x - min_x
    height = max_y - min_y
    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2
    print(f'{name} Cluster: {width:.1f} x {height:.1f} mm. Current Center: {cx:.1f}, {cy:.1f}')
