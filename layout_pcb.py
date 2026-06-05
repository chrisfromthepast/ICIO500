import pcbnew
import os

def apply_professional_layout():
    pcb_path = os.path.join(os.path.dirname(__file__), "build", "icio500", "icio500.kicad_pcb")
    if not os.path.exists(pcb_path):
        print("PCB not found.")
        return
        
    board = pcbnew.LoadBoard(pcb_path)

    print("Board loaded.")
    # Clean up old silkscreens we added
    labels = ["POWER SUPPLY", "INPUT STAGE", "OUTPUT STAGE", "SCALING OP-AMPS"]
    to_remove = []
    for item in board.GetDrawings():
        if isinstance(item, pcbnew.PCB_TEXT) and item.GetText() in labels:
            to_remove.append(item)
        elif isinstance(item, pcbnew.PCB_SHAPE) and item.GetLayer() == pcbnew.F_SilkS and item.GetWidth() == int(0.2 * 1000000):
            to_remove.append(item)
    for item in to_remove:
        board.Remove(item)
    print(f"Removed {len(to_remove)} old drawings.")
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    if 'J1' not in fps:
        print("J1 not found!")
        return

    anchor_fp = fps['J1']
    anchor_pos = anchor_fp.GetPosition()
    
    pads = {pad.GetName(): pad for pad in anchor_fp.Pads()}
    def get_pad_pos(pad_name):
        if pad_name in pads:
            return pads[pad_name].GetPosition().x / 1000000.0, pads[pad_name].GetPosition().y / 1000000.0
        return anchor_pos.x / 1000000.0, anchor_pos.y / 1000000.0

    out_x, out_y = get_pad_pos('3')
    in_x, in_y = get_pad_pos('8')
    pwr_x, pwr_y = get_pad_pos('13')

    # Groups
    def place(ref, x_mm, y_mm, rot=0):
        if ref in fps:
            fp = fps[ref]
            fp.SetPosition(pcbnew.VECTOR2I(int(x_mm * 1000000), int(y_mm * 1000000)))
            fp.SetOrientationDegrees(rot)

    # Base X offset from the edge connector pads.
    # The edge connector pads are near the right edge. We want circuits right next to them.
    X_OFFSET = 20 # 20mm to the left of the pads

    # --- Driver Section (THAT1646) - Output Stage ---
    # Connected to pins 2, 3, 4
    dx = out_x - X_OFFSET
    dy = out_y
    
    dx_ic = 'U4' if 'U4' in fps else ('U4' if 'U4' in fps else 'U4')
    place(dx_ic, dx, dy, 270)
    place('C17', dx, dy - 5, 0)
    place('C18', dx, dy - 2.5, 0)
    place('C19', dx, dy + 2.5, 0)
    place('C20', dx, dy + 5, 0)
    place('C21', dx + 6, dy - 3, 0)
    place('C22', dx + 6, dy + 3, 0)
    place('C23', dx + 10, dy - 3, 0)
    place('R7', dx + 14, dy - 3, 0)
    place('C24', dx + 10, dy + 3, 0)
    place('R8', dx + 14, dy + 3, 0)

    # --- Receiver Section (THAT1200) - Input Stage ---
    # Connected to pins 7, 8, 9, 10
    rx = in_x - X_OFFSET
    ry = in_y
    
    rx_ic = 'U2' if 'U2' in fps else ('U5' if 'U5' in fps else 'U3')
    place(rx_ic, rx, ry, 270)
    place('D3', rx + 10, ry - 4, 90)
    place('D4', rx + 10, ry - 1, 90)
    place('D5', rx + 10, ry + 1, 90)
    place('D6', rx + 10, ry + 4, 90)
    place('C10', rx + 5, ry - 3, 0)
    place('C11', rx + 5, ry + 3, 0)
    place('C9', rx + 5, ry - 6, 0)
    place('C12', rx + 5, ry + 6, 0)
    place('C7', rx, ry - 4, 0)
    place('C8', rx, ry + 4, 0)
    place('R1', rx - 5, ry - 3, 0)
    place('R2', rx - 5, ry + 3, 0)

    # --- Power Supply Section ---
    # Connected to pins 12, 13, 14, 15
    px = pwr_x - X_OFFSET
    py = pwr_y
    
    place('U1', px, py, 90)
    place('D1', px - 8, py - 4, 0)
    place('D2', px - 8, py + 4, 0)
    place('C1', px - 4, py - 4, 0)
    place('C2', px - 4, py - 8, 0)
    place('C3', px - 4, py + 4, 0)
    place('C4', px - 4, py + 8, 0)
    place('C5', px + 6, py, 0)
    place('C6', px + 6, py + 4, 0)

    # --- Scaling Section (Op-Amps) ---
    # Placed left of the input stage
    sx = rx - 25
    sy = ry
    
    sx_ic = 'U3' if 'U3' in fps else 'U3'
    place(sx_ic, sx, sy, 270)
    place('C13', sx, sy - 4, 0)
    place('C14', sx, sy + 4, 0)
    place('C15', sx - 5, sy - 3, 0)
    place('R3', sx - 8, sy - 3, 0)
    place('R4', sx - 5, sy + 3, 0)
    place('C16', sx + 5, sy - 3, 0)
    place('R5', sx + 8, sy - 3, 0)
    place('R6', sx + 5, sy + 3, 0)

    def draw_bounding_box(group_refs, label_text):
        if not group_refs: return
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        for ref in group_refs:
            if ref in fps:
                fp = fps[ref]
                bb = fp.GetBoundingBox()
                min_x = min(min_x, bb.GetLeft())
                max_x = max(max_x, bb.GetRight())
                min_y = min(min_y, bb.GetTop())
                max_y = max(max_y, bb.GetBottom())
        if min_x == float('inf'): return
        
        margin = int(2.0 * 1000000)
        min_x -= margin
        max_x += margin
        min_y -= margin
        max_y += margin
        
        rect = pcbnew.PCB_SHAPE(board)
        rect.SetShape(pcbnew.SHAPE_T_RECT)
        rect.SetFilled(False)
        rect.SetStart(pcbnew.VECTOR2I(min_x, min_y))
        rect.SetEnd(pcbnew.VECTOR2I(max_x, max_y))
        rect.SetLayer(pcbnew.F_SilkS)
        rect.SetWidth(int(0.2 * 1000000))
        board.Add(rect)
        
        text = pcbnew.PCB_TEXT(board)
        text.SetText(label_text)
        text.SetPosition(pcbnew.VECTOR2I(min_x, min_y - int(1.0 * 1000000)))
        text.SetLayer(pcbnew.F_SilkS)
        text.SetTextSize(pcbnew.VECTOR2I(int(1.5 * 1000000), int(1.5 * 1000000)))
        text.SetTextThickness(int(0.3 * 1000000))
        board.Add(text)

    draw_bounding_box(['U1', 'D1', 'D2', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6'], "POWER SUPPLY")
    draw_bounding_box([rx_ic, 'D3', 'D4', 'D5', 'D6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'R1', 'R2'], "INPUT STAGE")
    draw_bounding_box([dx_ic, 'C17', 'C18', 'C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'R7', 'R8'], "OUTPUT STAGE")
    draw_bounding_box([sx_ic, 'C13', 'C14', 'C15', 'C16', 'R3', 'R4', 'R5', 'R6'], "SCALING OP-AMPS")

    pcbnew.SaveBoard(pcb_path, board)
    print("Perfectly aligned layout applied!")

if __name__ == "__main__":
    apply_professional_layout()
