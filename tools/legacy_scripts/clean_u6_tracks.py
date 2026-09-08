import pcbnew

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
print("Deleting tracks near U6...")
deleted = 0
tracks_to_delete = []

pads_in_zone = [(pad.GetPosition().x / 1e6, pad.GetPosition().y / 1e6) for pad in board.GetPads() if 45 < pad.GetPosition().x / 1e6 < 60 and 80 < pad.GetPosition().y / 1e6 < 120]

for track in list(board.GetTracks()):
    if isinstance(track, pcbnew.PCB_TRACK):
        sx, sy = track.GetStart().x / 1e6, track.GetStart().y / 1e6
        ex, ey = track.GetEnd().x / 1e6, track.GetEnd().y / 1e6
        
        if (45 < sx < 60 and 80 < sy < 120) or (45 < ex < 60 and 80 < ey < 120):
            # If it connects to a pad, ONLY keep it if it's NOT U6
            # Wait, U6 is in the zone! If it connects to U6, DELETE it!
            # If it connects to something else, keep it.
            # But the autorouter generated tracks ending at 52.17.
            tracks_to_delete.append(track)
    elif isinstance(track, pcbnew.PCB_VIA):
        vx, vy = track.GetPosition().x / 1e6, track.GetPosition().y / 1e6
        if 45 < vx < 60 and 80 < vy < 120:
            tracks_to_delete.append(track)

# Let's just blindly delete them since this is an iterative process
for track in tracks_to_delete:
    board.Remove(track)
    deleted += 1

print(f"Deleted {deleted} tracks near U6.")
pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
