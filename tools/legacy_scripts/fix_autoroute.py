import re

with open('tools/legacy_scripts/autoroute_sat.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix the end points by making the last segment end at the target pad exact pos!
# In autoroute_sat.py around line 330:
#                 board.Add(track)
#             
#             print(f"    Path found: {len(path)} cells -> {len(waypoints)} waypoints")

fix = """
                if i == len(waypoints) - 1:
                    track.SetEnd(pcbnew.VECTOR2I_MM(target_pt[0], target_pt[1]))
                board.Add(track)
            
            # Also need to connect start point
            start_track = pcbnew.PCB_TRACK(board)
            start_track.SetStart(pcbnew.VECTOR2I_MM(start_pt[0], start_pt[1]))
            start_track.SetEnd(pcbnew.VECTOR2I_MM(waypoints[0][0], waypoints[0][1]))
            start_track.SetWidth(pcbnew.FromMM(TRACE_WIDTH))
            start_track.SetLayer(layer)
            start_track.SetNetCode(net)
            board.Add(start_track)
            
            print(f"    Path found: {len(path)} cells -> {len(waypoints)} waypoints")
"""

text = re.sub(r'\s*board\.Add\(track\)\s+print\(f"    Path found.*', fix, text)

with open('tools/legacy_scripts/autoroute_sat.py', 'w', encoding='utf-8') as f:
    f.write(text)

