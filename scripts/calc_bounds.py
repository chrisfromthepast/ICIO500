import pcbnew
import os

def get_bounds(board, refs):
    min_x = float('inf')
    max_x = -float('inf')
    min_y = float('inf')
    max_y = -float('inf')
    
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref in refs:
            bbox = fp.GetBoundingBox()
            left = bbox.GetLeft() / 1000000.0
            right = bbox.GetRight() / 1000000.0
            top = bbox.GetTop() / 1000000.0
            bottom = bbox.GetBottom() / 1000000.0
            
            if left < min_x: min_x = left
            if right > max_x: max_x = right
            if top < min_y: min_y = top
            if bottom > max_y: max_y = bottom
            
    return (min_x, max_x, min_y, max_y)

def main():
    pcb_path = os.path.join(
        os.getcwd(),
        "build", "icio500", "icio500.kicad_pcb"
    )
    board = pcbnew.LoadBoard(pcb_path)
    
    sections = {
        "OUTPUT STAGE": ["U4", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "R7", "R8"],
        "INPUT STAGE": ["U2", "C7", "C8", "C9", "C10", "C11", "C12", "C13", "C14", "R1", "R2", "D3", "D4", "D5", "D6"],
        "LEVEL SCALING": ["U3", "C15", "C16", "C17", "C18", "R3", "R4", "R5", "R6"],
        "ANALOG PSU": ["D1", "D2", "C1", "C2", "C3", "C4"],
        "ISOLATED POWER": ["U1", "C5", "C6"],
        "DAISY DIGITAL": ["U5", "U6", "U7", "J6", "J7"]
    }
    
    for name, refs in sections.items():
        min_x, max_x, min_y, max_y = get_bounds(board, refs)
        print(f"{name}: X({min_x:.1f} to {max_x:.1f}), Y({min_y:.1f} to {max_y:.1f})")

if __name__ == '__main__':
    main()
