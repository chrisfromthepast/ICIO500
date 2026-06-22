import pcbnew

board_path = 'build/icio500/icio500.kicad_pcb'
board = pcbnew.LoadBoard(board_path)

gnd_net = None
for net in board.GetNetsByName().values():
    if net.GetNetname() == "gnd":
        gnd_net = net
        break

tracks = board.GetTracks()
to_remove = []

for track in tracks:
    # Remove tracks and vias that are NOT ground
    if track.GetNetCode() != gnd_net.GetNetCode():
        to_remove.append(track)

for item in to_remove:
    board.Remove(item)

pcbnew.SaveBoard(board_path, board)
print(f"Cleared {len(to_remove)} signal tracks/vias, kept ground fanout intact!")
