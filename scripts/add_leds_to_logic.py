import pcbnew
import traceback

def add_led_pad(board, ref, x, y):
    # Create a simple copper pad (1.6mm diameter) to represent an SMD LED
    pad = pcbnew.PAD(board)
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetSize(pcbnew.VECTOR2I(int(1.6 * 1e6), int(1.6 * 1e6)))
    pad.SetDrillSize(pcbnew.VECTOR2I(int(0.8 * 1e6), int(0.8 * 1e6)))
    pad.SetLayerSet(pcbnew.LSET(pcbnew.F_Cu))
    pad.SetPosition(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)))
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    # Attach a reference/name via a dummy footprint container (optional)
    board.Add(pad)

def main():
    board = pcbnew.LoadBoard('build/icio500/faceplate_logic.kicad_pcb')
    # Clean any existing SMD pads we might have added before (heuristic by size)
    for pad in list(board.GetPads()):
        if pad.GetSizeX() == int(1.6 * 1e6) and pad.GetSizeY() == int(1.6 * 1e6):
            board.RemoveNative(pad)
    knob_x = 19.05
    start_y = 86.0
    pitch = 8.0
    for i in range(10):
        y = start_y - i * pitch
        add_led_pad(board, f'LED{i+1}', knob_x, y)
    # Encoder under‑light pad (6 mm dia)
    enc_pad = pcbnew.PAD(board)
    enc_pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    enc_pad.SetSize(pcbnew.VECTOR2I(int(6.0 * 1e6), int(6.0 * 1e6)))
    enc_pad.SetDrillSize(pcbnew.VECTOR2I(int(0), int(0)))
    enc_pad.SetLayerSet(pcbnew.LSET(pcbnew.F_Cu))
    enc_pad.SetPosition(pcbnew.VECTOR2I(int(knob_x * 1e6), int(109.35 * 1e6)))
    enc_pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    board.Add(enc_pad)
    pcbnew.SaveBoard('build/icio500/faceplate_logic.kicad_pcb', board)
    print('Logic board padded with LEDs and encoder hole')

if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
