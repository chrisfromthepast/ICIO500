import pcbnew
import os
import sys

board_path = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\faceplate\faceplate.kicad_pcb"
mod_dir = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\elec\footprints\ICIO500.pretty"

try:
    board = pcbnew.LoadBoard(board_path)
    
    # 1. Load the new D-Series footprint
    fp = pcbnew.FootprintLoad(mod_dir, "Neutrik_D_Series_PanelCutout")
    if not fp:
        print("Could not load footprint.")
        sys.exit(1)
        
    fp.SetReference("J_D_SERIES")
    board.Add(fp)
    
    # 2. Get board dimensions to place things
    bbox = board.GetBoardEdgesBoundingBox()
    center_x = bbox.GetX() + (bbox.GetWidth() // 2)
    top_y = bbox.GetY()
    bottom_y = bbox.GetY() + bbox.GetHeight()
    
    # 500-series faceplate is usually ~38mm wide, ~133mm tall.
    # Put the massive D-Series connector at the bottom (Y = bottom - 25mm)
    fp.SetPosition(pcbnew.VECTOR2I(center_x, bottom_y - int(25 * 1e6)))
    
    # 3. Move the Encoder and LEDs UP to make room
    encoder_ref = "encoder"
    # Actually let's find the encoder and LEDs and just shift them up by 30mm
    for f in board.GetFootprints():
        ref = f.GetReference()
        if "led" in ref.lower() or "encoder" in ref.lower():
            # Shift up by 30mm
            pos = f.GetPosition()
            f.SetPosition(pcbnew.VECTOR2I(pos.x, pos.y - int(30 * 1e6)))
            
    board.Save(board_path)
    print("Successfully added D-Series cutout and shifted components UP by 30mm!")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
