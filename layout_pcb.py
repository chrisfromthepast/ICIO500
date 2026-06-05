import pcbnew
import os

def apply_professional_layout():
    pcb_path = os.path.join(os.path.dirname(__file__), "build", "icio500", "icio500.kicad_pcb")
    
    if not os.path.exists(pcb_path):
        print("Please save the KiCad board from your open KiCad window to restore the file!")
        return
        
    board = pcbnew.LoadBoard(pcb_path)

    # Find J1 (edge connector) to use as the reference anchor.
    # Do NOT move J1, and do NOT delete Edge.Cuts!
    anchor_fp = None
    edge_con = []
    power = []
    that1200 = []
    scaling = []
    that1600 = []

    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref == 'J1':
            anchor_fp = fp
            edge_con.append(fp)
        elif ref == 'U1':
            edge_con.append(fp)
        elif ref in ['D1', 'D2', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6']:
            power.append(fp)
        elif ref in ['U3', 'D3', 'D4', 'D5', 'D6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'R1', 'R2']:
            that1200.append(fp)
        elif ref in ['U4', 'C17', 'C18', 'C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'R7', 'R8']:
            scaling.append(fp)
        elif ref in ['U5', 'C13', 'C14', 'C15', 'C16', 'R5', 'R6', 'R3', 'R4']:
            that1600.append(fp)
        else:
            scaling.append(fp)

    if not anchor_fp:
        print("Error: Could not find J1 to use as anchor.")
        return
        
    # J1 is on the right edge of the board. Board extends to the LEFT.
    anchor_pos = anchor_fp.GetPosition()
    ANCHOR_X = anchor_pos.x / 1000000.0
    ANCHOR_Y = anchor_pos.y / 1000000.0
    
    # We will place components starting from the front panel (Left side) moving Right towards J1.
    def place_group(group, start_x_mm, start_y_mm, columns=4, spacing_x_mm=12, spacing_y_mm=12):
        sorted_group = sorted(group, key=lambda x: x.GetReference())
        # Filter out J1 from being moved
        sorted_group = [fp for fp in sorted_group if fp.GetReference() != 'J1']
        for i, fp in enumerate(sorted_group):
            row = i // columns
            col = i % columns
            pos = pcbnew.VECTOR2I(
                int((start_x_mm + col * spacing_x_mm) * 1000000),
                int((start_y_mm + row * spacing_y_mm) * 1000000)
            )
            fp.SetPosition(pos)
            fp.SetOrientationDegrees(0)
            
    # 1. THAT1200 Input Stage at the front left
    place_group(that1200, ANCHOR_X - 130, ANCHOR_Y - 50, columns=3, spacing_x_mm=15, spacing_y_mm=15)

    # 2. Active Scaling Stage in the middle
    place_group(scaling, ANCHOR_X - 90, ANCHOR_Y - 50, columns=3, spacing_x_mm=15, spacing_y_mm=15)

    # 3. THAT1646 Output Stage on the right (before J1)
    place_group(that1600, ANCHOR_X - 50, ANCHOR_Y - 50, columns=3, spacing_x_mm=15, spacing_y_mm=15)

    # 4. Power section near J1
    place_group(power, ANCHOR_X - 50, ANCHOR_Y + 10, columns=4, spacing_x_mm=12, spacing_y_mm=12)
    
    if 'U1' in [fp.GetReference() for fp in edge_con]:
        u1_fp = next(fp for fp in edge_con if fp.GetReference() == 'U1')
        u1_fp.SetPosition(pcbnew.VECTOR2I(int((ANCHOR_X - 25) * 1000000), int((ANCHOR_Y + 30) * 1000000)))

    pcbnew.SaveBoard(pcb_path, board)
    print("Updated layout applied relative to J1!")

if __name__ == "__main__":
    apply_professional_layout()
