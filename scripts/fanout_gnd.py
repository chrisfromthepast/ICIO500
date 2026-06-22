import pcbnew
import math

board_path = 'build/icio500/icio500.kicad_pcb'
board = pcbnew.LoadBoard(board_path)

gnd_net = None
for net in board.GetNetsByName().values():
    if net.GetNetname() == "gnd":
        gnd_net = net
        break

if not gnd_net:
    print("Could not find gnd net")
    exit(1)

# Remove the keepout zone we added previously to In1.Cu so the ground plane can be solid
zones_to_remove = []
for zone in board.Zones():
    if zone.GetIsRuleArea() and zone.GetLayer() == pcbnew.In1_Cu:
        zones_to_remove.append(zone)
for zone in zones_to_remove:
    board.Remove(zone)

print(f"Removed {len(zones_to_remove)} keepouts")

pads_fanned_out = 0
for pad in board.GetPads():
    if pad.GetNetCode() == gnd_net.GetNetCode():
        # If it's a surface mount pad on F.Cu or B.Cu
        if pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD:
            # We need to drop a via next to it.
            # Calculate a position slightly outside the pad
            # We'll just place it 1.5mm away in the direction of its longest dimension or just arbitrary
            pos = pad.GetPosition()
            
            # Create a via
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(pcbnew.VECTOR2I(pos.x + pcbnew.FromMM(1.2), pos.y + pcbnew.FromMM(1.2)))
            via.SetNetCode(gnd_net.GetNetCode())
            via.SetDrill(pcbnew.FromMM(0.3))
            via.SetWidth(pcbnew.FromMM(0.6))
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            board.Add(via)
            
            # Create a track from pad to via
            track = pcbnew.PCB_TRACK(board)
            track.SetStart(pos)
            track.SetEnd(via.GetPosition())
            track.SetWidth(pcbnew.FromMM(0.25))
            track.SetLayer(pad.GetLayer())
            track.SetNetCode(gnd_net.GetNetCode())
            board.Add(track)
            
            pads_fanned_out += 1

# Refill the ground plane!
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

pcbnew.SaveBoard(board_path, board)
print(f"Fanned out {pads_fanned_out} SMD ground pads to the internal plane!")
