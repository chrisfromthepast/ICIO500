import pcbnew
import math

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

print("Deleting dangling tracks...")
deleted = 0
tracks_to_delete = []
for track in list(board.GetTracks()):
    if isinstance(track, pcbnew.PCB_TRACK):
        sx, sy = track.GetStart().x / 1e6, track.GetStart().y / 1e6
        ex, ey = track.GetEnd().x / 1e6, track.GetEnd().y / 1e6
        
        if (85 < sx < 100 and 90 < sy < 120) or (85 < ex < 100 and 90 < ey < 120):
            tracks_to_delete.append(track)
            
    elif isinstance(track, pcbnew.PCB_VIA):
        vx, vy = track.GetPosition().x / 1e6, track.GetPosition().y / 1e6
        if 85 < vx < 100 and 90 < vy < 120:
            tracks_to_delete.append(track)

# Let's just delete all tracks and vias in that zone for simplicity,
# assuming we don't accidentally delete anything important! 
# Wait, are there other components in that zone?
# Let's check components in that zone!
for pad in board.GetPads():
    px, py = pad.GetPosition().x / 1e6, pad.GetPosition().y / 1e6
    if 85 < px < 100 and 90 < py < 120:
        print(f"Pad {pad.GetParent().GetReference()} is in zone!")

# Let's only delete if they are NOT on a pad!
pads_in_zone = [(pad.GetPosition().x / 1e6, pad.GetPosition().y / 1e6) for pad in board.GetPads() if 85 < pad.GetPosition().x / 1e6 < 100 and 90 < pad.GetPosition().y / 1e6 < 120]

for track in tracks_to_delete:
    if isinstance(track, pcbnew.PCB_TRACK):
        sx, sy = track.GetStart().x / 1e6, track.GetStart().y / 1e6
        ex, ey = track.GetEnd().x / 1e6, track.GetEnd().y / 1e6
        
        start_on_pad = any(abs(px - sx) < 0.1 and abs(py - sy) < 0.1 for px, py in pads_in_zone)
        end_on_pad = any(abs(px - ex) < 0.1 and abs(py - ey) < 0.1 for px, py in pads_in_zone)
        
        # If it's a via, it only has one pos.
        if not (start_on_pad and end_on_pad):
            board.Remove(track)
            deleted += 1
    elif isinstance(track, pcbnew.PCB_VIA):
        vx, vy = track.GetPosition().x / 1e6, track.GetPosition().y / 1e6
        on_pad = any(abs(px - vx) < 0.1 and abs(py - vy) < 0.1 for px, py in pads_in_zone)
        if not on_pad:
            board.Remove(track)
            deleted += 1

print(f"Deleted {deleted} tracks near old U6.")
pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
