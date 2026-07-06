import pcbnew

def add_led_window(board, x, y, width, height):
    layers = [pcbnew.F_Mask, pcbnew.B_Mask, pcbnew.Dwgs_User]
    for layer in layers:
        shape = pcbnew.PCB_SHAPE(board)
        shape.SetShape(pcbnew.S_RECT)
        shape.SetLayer(layer)
        shape.SetWidth(int(0.1 * 1e6))
        shape.SetFilled(True)
        shape.SetStart(pcbnew.VECTOR2I(int((x - width/2) * 1e6), int((y - height/2) * 1e6)))
        shape.SetEnd(pcbnew.VECTOR2I(int((x + width/2) * 1e6), int((y + height/2) * 1e6)))
        board.Add(shape)

def add_encoder_window(board, x, y, radius):
    layers = [pcbnew.F_Mask, pcbnew.B_Mask]
    for layer in layers:
        shape = pcbnew.PCB_SHAPE(board)
        shape.SetShape(pcbnew.S_CIRCLE)
        shape.SetLayer(layer)
        shape.SetWidth(int(0.1 * 1e6))
        shape.SetFilled(True)
        shape.SetCenter(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)))
        shape.SetEnd(pcbnew.VECTOR2I(int((x + radius) * 1e6), int(y * 1e6)))
        board.Add(shape)

def main():
    board = pcbnew.LoadBoard('build/icio500/faceplate_front.kicad_pcb')
    
    # 1. Clean up old windows
    for dwg in list(board.GetDrawings()):
        if dwg.GetLayer() != pcbnew.Edge_Cuts:
            board.RemoveNative(dwg)
            
    # Bottom knob position
    knob_x = 19.05
    knob_y = 109.35
    
    # Add LED windows (10 LEDs, spaced to fill the top half!)
    # Width 12.0mm, Height 4.0mm, Pitch 8.0mm
    for i in range(10):
        led_y = 86.0 - (i * 8.0)
        add_led_window(board, knob_x, led_y, 12.0, 4.0)
        
    # Add Encoder shaft window
    add_encoder_window(board, knob_x, knob_y, 3.5)
            
    pcbnew.SaveBoard('build/icio500/faceplate_front.kicad_pcb', board)
    print("Fixed LED windows spacing!")

if __name__ == '__main__':
    main()
