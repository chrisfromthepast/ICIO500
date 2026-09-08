import re

with open('tools/legacy_scripts/autoroute_sat.py', 'r', encoding='utf-8') as f:
    text = f.read()

# The function that generates the segments:
#     for pair in to_route:
#         pad1_id, pad2_id = pair
#         p1 = pad_dict[pad1_id]
#         p2 = pad_dict[pad2_id]
#         ...
#         waypoints = ...
# Then it does:
#             sx, sy = grid.rc_to_xy(prev[0], prev[1])
#             ex, ey = grid.rc_to_xy(curr[0], curr[1])

# We need to change the first sx,sy to p1['x'], p1['y']
# and the last ex,ey to p2['x'], p2['y']

fix = """
        print(f"    Path found: {len(path)} cells -> {len(waypoints)} waypoints")
        
        # FIX ENDPOINTS
        for i in range(1, len(waypoints)):
            prev = waypoints[i-1]
            curr = waypoints[i]
            
            sx, sy = grid.rc_to_xy(prev[0], prev[1])
            ex, ey = grid.rc_to_xy(curr[0], curr[1])
            
            if i == 1:
                sx, sy = p1['x'], p1['y']
            if i == len(waypoints) - 1:
                ex, ey = p2['x'], p2['y']
                
            if prev[2] != curr[2]:
                # Add via
                nid = next((nid for nn, nid in grid.net_to_id.items() if nn == net), 0)
                new_segments.append(f'  (via (at {sx:.3f} {sy:.3f}) (size 0.8) (drill 0.4) (layers "F.Cu" "B.Cu") (net {nid}))')
            else:
                # Add segment
                new_segments.append(make_segment(sx, sy, ex, ey, net, width, curr[2]))
                grid.mark_line(curr[2], sx, sy, ex, ey, width + CLEARANCE * 2, net)
"""

text = re.sub(r'        print\(f"    Path found: \{len\(path\)\} cells -> \{len\(waypoints\)\} waypoints"\)[\s\S]*?(?=        # Update endpoints)', fix, text)

with open('tools/legacy_scripts/autoroute_sat_fixed.py', 'w', encoding='utf-8') as f:
    f.write(text)

