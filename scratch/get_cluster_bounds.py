import pcbnew

board = pcbnew.LoadBoard('original_board.kicad_pcb')

def get_b(refs):
    min_x, min_y, max_x, max_y = 1e9, 1e9, -1e9, -1e9
    for ref in refs:
        fp = board.FindFootprintByReference(ref)
        if fp:
            rect = fp.GetBoundingBox()
            min_x = min(min_x, rect.GetX())
            min_y = min(min_y, rect.GetY())
            max_x = max(max_x, rect.GetRight())
            max_y = max(max_y, rect.GetBottom())
    if min_x == 1e9: return "Not found"
    return f"X: {min_x/1e6:.1f} to {max_x/1e6:.1f}, Y: {min_y/1e6:.1f} to {max_y/1e6:.1f}"

print("POWER (Core):", get_b(["U1", "C1", "C2", "C3", "C4", "C5", "C6"]))
print("POWER (Diode):", get_b(["D1", "D2"]))
print("INPUT:", get_b(["U2", "R1", "R2", "C12", "C13", "C14", "C9", "C10", "C11", "D3", "D4", "D5", "D6", "C7", "C15", "C8", "C16"]))
print("SCALING:", get_b(["U3", "R3", "R4", "R5", "R6", "C17", "C18"]))
print("DRIVER:", get_b(["U4", "C19", "C20", "C21", "C22", "C23", "C24", "R7", "C25", "R8", "C26"]))
print("DIGITAL:", get_b(["U5", "U6", "U7"]))
