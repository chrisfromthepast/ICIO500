import pcbnew
import sys

def main():
    logic_board = pcbnew.LoadBoard('build/icio500/faceplate_logic.kicad_pcb')
    front_board = pcbnew.LoadBoard('build/icio500/faceplate_front.kicad_pcb')

    # 1. Update Logic Board
    # 10 LEDs (Y = 30 to 84, step 6)
    for i in range(1, 11):
        led = logic_board.FindFootprintByReference(f'led_bar_{i}')
        if led:
            led.SetPosition(pcbnew.VECTOR2I(int(21.05*1e6), int((30 + (i-1)*6)*1e6)))
            led.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
            led.SetLayer(pcbnew.F_Cu)

    # led_under (encoder LED)
    led_under = logic_board.FindFootprintByReference('led_under')
    if led_under:
        led_under.SetPosition(pcbnew.VECTOR2I(int(19.05*1e6), int(24.0*1e6)))
        led_under.SetLayer(pcbnew.F_Cu)
        
    led_drv = logic_board.FindFootprintByReference('led_drv')
    if led_drv:
        led_drv.SetPosition(pcbnew.VECTOR2I(int(15.0*1e6), int(55.0*1e6)))
        led_drv.SetLayer(pcbnew.F_Cu)
        
    pcbnew.SaveBoard('build/icio500/faceplate_logic.kicad_pcb', logic_board)

    # 2. Update Front Board
    # Remove old LED Edge.Cuts holes (Y=40, 46, 52, 58)
    for dwg in list(front_board.GetDrawings()):
        if isinstance(dwg, pcbnew.PCB_SHAPE) and dwg.GetShape() == pcbnew.SHAPE_T_CIRCLE:
            if dwg.GetLayer() == pcbnew.Edge_Cuts:
                center = dwg.GetCenter()
                y_mm = center.y / 1e6
                if y_mm in [40.0, 46.0, 52.0, 58.0]:
                    front_board.RemoveNative(dwg)

    # Add Z-Axis milling slot for LEDs (B.Mask and User.1)
    # A single large slot covering all 10 LEDs
    # X from 19.5 to 22.5, Y from 28 to 86
    slot_width = 3.0
    slot_height = 58.0
    slot_x = 21.05
    slot_y = 57.0 # Center of 28 to 86
    
    for layer in [pcbnew.B_Mask, pcbnew.User_1]:
        rect = pcbnew.PCB_SHAPE(front_board)
        rect.SetShape(pcbnew.SHAPE_T_RECT)
        rect.SetStart(pcbnew.VECTOR2I(int((slot_x - slot_width/2) * 1e6), int((slot_y - slot_height/2) * 1e6)))
        rect.SetEnd(pcbnew.VECTOR2I(int((slot_x + slot_width/2) * 1e6), int((slot_y + slot_height/2) * 1e6)))
        rect.SetLayer(layer)
        rect.SetWidth(0) # Filled
        front_board.Add(rect)
        
    # Add text note for Z-Axis milling
    txt = pcbnew.PCB_TEXT(front_board)
    txt.SetText("Z-AXIS MILLING: Mill from bottom to 0.4mm remaining thickness")
    txt.SetPosition(pcbnew.VECTOR2I(int(10.0 * 1e6), int(57.0 * 1e6)))
    txt.SetLayer(pcbnew.User_1)
    txt.SetTextSize(pcbnew.VECTOR2I(int(1e6), int(1e6)))
    front_board.Add(txt)

    # Add copper and silkscreen keepout under encoder (10mm circle)
    # Actually, KiCad handles keepouts with RULE AREAS.
    # We can just draw filled circles on B.Mask and F.Mask to ensure no mask, 
    # and no copper should be poured there.
    
    pcbnew.SaveBoard('build/icio500/faceplate_front.kicad_pcb', front_board)
    print("Successfully laid out iteration 2!")

if __name__ == "__main__":
    main()
