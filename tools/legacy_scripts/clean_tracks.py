import pcbnew
import math

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

# old U6 was at X=93, Y=103.825
# it has 20 pins, mostly spanning X=85 to 100, Y=90 to 120
# Let's just find any track endpoint that is within this box, and if it's not connected to a pad, delete it!

print("Deleting dangling tracks...")
deleted = 0
for track in list(board.GetTracks()):
    sx, sy = track.GetStart().x / 1e6, track.GetStart().y / 1e6
    ex, ey = track.GetEnd().x / 1e6, track.GetEnd().y / 1e6
    
    # Check if either end is near the old U6 area
    if (85 < sx < 100 and 90 < sy < 120) or (85 < ex < 100 and 90 < ey < 120):
        # We don't want to delete tracks that are actually connected to valid pads.
        # So let's check if the endpoints are on any pad.
        start_on_pad = False
        end_on_pad = False
        for pad in board.GetPads():
            px, py = pad.GetPosition().x / 1e6, pad.GetPosition().y / 1e6
            if abs(px - sx) < 0.1 and abs(py - sy) < 0.1:
                start_on_pad = True
            if abs(px - ex) < 0.1 and abs(py - ey) < 0.1:
                end_on_pad = True
        
        if not start_on_pad or not end_on_pad:
            board.Remove(track)
            deleted += 1

print(f"Deleted {deleted} tracks near old U6.")
pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
