import sys
import traceback

try:
    import pcbnew
    board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

    u6 = board.FindFootprintByReference('U6')
    if not u6:
        print('U6 not found')
        sys.exit(1)

    # Shift U6 by 3.83mm right
    shift_x = 3.83 * 1e6
    old_pos = u6.GetPosition()
    u6.SetPosition(pcbnew.VECTOR2I(int(old_pos.x + shift_x), old_pos.y))

    added = 0
    for pad in u6.Pads():
        px, py = pad.GetPosition().x, pad.GetPosition().y
        
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(pcbnew.VECTOR2I(int(px - shift_x), int(py)))
        track.SetEnd(pcbnew.VECTOR2I(int(px), int(py)))
        track.SetWidth(int(0.25 * 1e6))
        
        net = pad.GetNetname()
        if net in ['gnd', 'GND', 'v_plus', 'v_minus', 'daisy_5v_power', '+3V3', '+3V3_IN']:
            track.SetWidth(int(0.4 * 1e6))
            
        track.SetLayer(pcbnew.F_Cu)
        board.Add(track)
        added += 1

    print(f"Moved U6 and added {added} extension tracks.")
    pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
except Exception as e:
    print('Error:', e)
    traceback.print_exc()
