import pcbnew
import os

def mm(v):
    return int(v * 1_000_000)

def clean_silkscreen():
    pcb_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "build", "icio500", "icio500.kicad_pcb"
    )
    board = pcbnew.LoadBoard(pcb_path)
    print("Board loaded for silkscreen cleanup.")

    for fp in board.GetFootprints():
        # Hide only invalid value fields (the "?" clutter), restore IC names
        val = fp.Value()
        if val:
            text = val.GetText().strip()
            if text in ['?', '~', ''] or text.startswith('?'):
                val.SetVisible(False)
            else:
                val.SetVisible(True)
                val.SetTextSize(pcbnew.VECTOR2I(mm(0.6), mm(0.6)))
                val.SetTextThickness(mm(0.12))
                val.SetLayer(pcbnew.F_SilkS)
        
        # Normalize the reference designator size
        ref = fp.Reference()
        if ref:
            ref.SetVisible(True)
            ref.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
            ref.SetTextThickness(mm(0.12))
            # Make sure it's on the front silkscreen
            ref.SetLayer(pcbnew.F_SilkS)

    pcbnew.SaveBoard(pcb_path, board)
    print("Silkscreen cleaned: Values hidden, References normalized.")

if __name__ == '__main__':
    clean_silkscreen()
