import pcbnew
import math

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
u6 = board.FindFootprintByReference('U6')

net_pads = {}
for pad in board.GetPads():
    if pad.GetParent().GetReference() == 'U6': continue
    net = pad.GetNetname()
    if net == "daisy_5v_power":
        if net not in net_pads: net_pads[net] = []
        net_pads[net].append(pad)

added = 0
for pad in u6.Pads():
    if pad.GetNetname() == "daisy_5v_power":
        px, py = pad.GetPosition().x, pad.GetPosition().y
        tx, ty = net_pads["daisy_5v_power"][0].GetPosition().x, net_pads["daisy_5v_power"][0].GetPosition().y
        
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(pcbnew.VECTOR2I(int(px), int(py)))
        track.SetEnd(pcbnew.VECTOR2I(int(tx), int(ty)))
        track.SetWidth(int(0.4 * 1e6))
        track.SetLayer(pcbnew.B_Cu)
        board.Add(track)
        added += 1

print(f"Added {added} straight-line tracks.")
pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
