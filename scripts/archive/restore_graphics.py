import pcbnew

def main():
    old_board = pcbnew.LoadBoard('temp_repo/build/icio500/faceplate_front.kicad_pcb')
    new_board = pcbnew.LoadBoard('build/icio500/faceplate_front.kicad_pcb')
    
    # 1. Restore the "cool stuff around the encoder"
    # This means PCB_SHAPEs on F.Cu and F.Mask that are between Y=15 and Y=37.
    for dwg in old_board.GetDrawings():
        if isinstance(dwg, pcbnew.PCB_SHAPE):
            layer = dwg.GetLayerName()
            if layer in ['F.Cu', 'F.Mask']:
                # The encoder is at Y=24. The graphics around it are roughly Y=15 to Y=37.
                # If we use GetBoundingBox(), we can check if it's in this region.
                bbox = dwg.GetBoundingBox()
                c_y = bbox.GetCenter().y / 1e6
                if 15.0 <= c_y <= 37.0:
                    new_s = dwg.Duplicate()
                    new_board.Add(pcbnew.Cast_to_BOARD_ITEM(new_s))
                    
    # 2. Add Metering Text next to the 10 LEDs!
    # LEDs are at Y = 30 + (i-1)*6. 
    # Y=84 is bottom (LED 1). Y=30 is top (LED 10).
    labels = {
        84.0: "-40",
        72.0: "-20",
        60.0: "-12",
        48.0: "-6",
        30.0: "CLIP"
    }
    
    for y, text in labels.items():
        txt = pcbnew.PCB_TEXT(new_board)
        txt.SetText(text)
        txt.SetPosition(pcbnew.VECTOR2I(int(18.0 * 1e6), int(y * 1e6)))
        txt.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_RIGHT)
        txt.SetLayer(pcbnew.F_SilkS)
        txt.SetTextSize(pcbnew.VECTOR2I(int(1.2 * 1e6), int(1.2 * 1e6)))
        txt.SetTextThickness(int(0.2 * 1e6))
        new_board.Add(txt)
            
    pcbnew.SaveBoard('build/icio500/faceplate_front.kicad_pcb', new_board)
    print("Successfully restored encoder graphics and added metering labels!")

if __name__ == "__main__":
    main()
