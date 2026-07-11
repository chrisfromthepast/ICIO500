import pcbnew
import math

def add_led_window(board, x, y, width, height):
    layers = [pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.F_Mask, pcbnew.B_Mask, pcbnew.User_1]
    for layer in layers:
        shape = pcbnew.PCB_SHAPE(board)
        shape.SetShape(pcbnew.S_RECT)
        shape.SetLayer(layer)
        shape.SetWidth(int(0.1 * 1e6))
        shape.SetFilled(True)
        # S_RECT uses SetStart and SetEnd
        shape.SetStart(pcbnew.VECTOR2I(int((x - width/2) * 1e6), int((y - height/2) * 1e6)))
        shape.SetEnd(pcbnew.VECTOR2I(int((x + width/2) * 1e6), int((y + height/2) * 1e6)))
        board.Add(shape)

def add_encoder_window(board, x, y, radius):
    layers = [pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.F_Mask, pcbnew.B_Mask]
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
    
    # Bottom knob position
    knob_x = 19.05
    knob_y = 109.35
    
    # Add LED windows (10 LEDs, spaced 5mm apart, going UP)
    # 8mm wide, 3mm tall
    for i in range(10):
        led_y = knob_y - 15.0 - (i * 5.0)
        add_led_window(board, knob_x, led_y, 8.0, 3.0)
        
    # Add Encoder shaft window
    add_encoder_window(board, knob_x, knob_y, 3.0) # 6mm diameter
    
    # Move the geometric graphic to the new knob_y!
    for fp in list(board.GetFootprints()):
        if 'EncoderGraphic' in fp.GetFPID().GetLibItemName().c_str():
            fp.SetPosition(pcbnew.VECTOR2I(int(knob_x * 1e6), int(knob_y * 1e6)))
            
    pcbnew.SaveBoard('build/icio500/faceplate_front.kicad_pcb', board)
    print("Added LED windows and moved graphic to bottom!")

if __name__ == '__main__':
    main()
