import os
import sys
import pcbnew
import math

def main():
    board_path = 'build/icio500/faceplate_front.kicad_pcb'
    b = pcbnew.LoadBoard(board_path)
    
    # 1. Delete all PCB_TEXT
    for dwg in list(b.GetDrawings()):
        if isinstance(dwg, pcbnew.PCB_TEXT):
            b.RemoveNative(dwg)
            
    # 2. Delete U4 and C3
    for ref in ['U4', 'C3']:
        fp = b.FindFootprintByReference(ref)
        if fp:
            b.RemoveNative(fp)
            
    # 3. Add Encoder Hole (Radius 3.5mm at 19.05, 24.0)
    encoder_circle = pcbnew.PCB_SHAPE(b)
    encoder_circle.SetShape(pcbnew.SHAPE_T_CIRCLE)
    encoder_circle.SetCenter(pcbnew.VECTOR2I(int(19.05 * 1e6), int(24.0 * 1e6)))
    encoder_circle.SetEnd(pcbnew.VECTOR2I(int((19.05 + 3.5) * 1e6), int(24.0 * 1e6)))
    encoder_circle.SetLayer(pcbnew.Edge_Cuts)
    encoder_circle.SetWidth(int(0.1 * 1e6))
    b.Add(encoder_circle)
    
    # 4. Add LED Holes (Radius 1.5mm)
    led_ys = [40.0, 46.0, 52.0, 58.0]
    for y in led_ys:
        led_circle = pcbnew.PCB_SHAPE(b)
        led_circle.SetShape(pcbnew.SHAPE_T_CIRCLE)
        led_circle.SetCenter(pcbnew.VECTOR2I(int(21.05 * 1e6), int(y * 1e6)))
        led_circle.SetEnd(pcbnew.VECTOR2I(int((21.05 + 1.5) * 1e6), int(y * 1e6)))
        led_circle.SetLayer(pcbnew.Edge_Cuts)
        led_circle.SetWidth(int(0.1 * 1e6))
        b.Add(led_circle)
        
    pcbnew.SaveBoard(board_path, b)
    print("Successfully updated the faceplate with physical holes and removed labels.")

if __name__ == "__main__":
    main()
