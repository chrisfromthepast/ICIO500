import pcbnew

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

def get_bounds(refs):
    min_x, min_y, max_x, max_y = 1e9, 1e9, -1e9, -1e9
    for ref in refs:
        fp = board.FindFootprintByReference(ref)
        if fp:
            rect = fp.GetBoundingBox()
            min_x = min(min_x, rect.GetX())
            min_y = min(min_y, rect.GetY())
            max_x = max(max_x, rect.GetRight())
            max_y = max(max_y, rect.GetBottom())
    return (min_x/1e6, min_y/1e6, max_x/1e6, max_y/1e6)

print("POWER:", get_bounds(["U1", "C1", "C2", "C3", "C4", "C5", "C6", "D1", "D2", "U8"]))
print("INPUT:", get_bounds(["U2", "R1", "R2", "C12", "C13", "C14", "C9", "C10", "C11", "D3", "D4", "D5", "D6", "C7", "C15", "C8", "C16"]))
print("SCALING:", get_bounds(["U3", "R3", "R4", "R5", "R6", "C17", "C18"]))
print("DRIVER:", get_bounds(["U4", "C19", "C20", "C21", "C22", "C23", "C24", "R7", "C25", "R8", "C26"]))
print("DIGITAL:", get_bounds(["U5", "U6", "U7"]))
