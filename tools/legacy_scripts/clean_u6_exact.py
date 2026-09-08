import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

u6 = board.FindFootprintByReference('U6')
if not u6: exit(1)
u6_pads = [(p.GetPosition().x/1e6, p.GetPosition().y/1e6) for p in u6.Pads()]

deleted = 0
for track in list(board.GetTracks()):
    if isinstance(track, pcbnew.PCB_TRACK):
        sx, sy = track.GetStart().x/1e6, track.GetStart().y/1e6
        ex, ey = track.GetEnd().x/1e6, track.GetEnd().y/1e6
        
        # if either end is exactly on a U6 pad
        on_u6 = False
        for px, py in u6_pads:
            if abs(px - sx) < 0.05 and abs(py - sy) < 0.05: on_u6 = True
            if abs(px - ex) < 0.05 and abs(py - ey) < 0.05: on_u6 = True
        
        if on_u6:
            board.Remove(track)
            deleted += 1

print(f"Deleted {deleted} tracks connected to U6.")
pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
