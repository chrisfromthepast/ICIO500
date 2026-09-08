import pcbnew
import math

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

# Unroute old traces connected to U6
for track in list(board.GetTracks()):
    if track.GetStart().x / 1e6 > 90 and track.GetStart().y / 1e6 > 100:
        pass # we don't know exactly which tracks, so let's just use the autorouter to route the unconnected nets!

# Wait, if we don't delete the old tracks, we will have dangling tracks and DRC errors!
# Let's delete ALL tracks that are not connected to anything (dangling) or just clear tracks in the U6 area!
