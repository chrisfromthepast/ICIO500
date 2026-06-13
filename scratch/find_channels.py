import pcbnew

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

# Define the region of interest
min_x, max_x = 150.0, 172.0
min_y, max_y = 80.0, 95.0

bcu_items = []

for track in board.GetTracks():
    if track.GetLayer() == pcbnew.B_Cu or track.GetLayer() == pcbnew.F_Cu or track.GetLayer() == pcbnew.B_Mask: # vias are on all layers, tracks on B_Cu
        if hasattr(track, 'GetStart'):
            s = track.GetStart()
            e = track.GetEnd()
            w = track.GetWidth()
            sx, sy = s.x / 1e6, s.y / 1e6
            ex, ey = e.x / 1e6, e.y / 1e6
            
            # check if in region
            if max(sx, ex) > min_x and min(sx, ex) < max_x and max(sy, ey) > min_y and min(sy, ey) < max_y:
                bcu_items.append({
                    'type': 'track',
                    'layer': track.GetLayerName(),
                    'sx': sx, 'sy': sy, 'ex': ex, 'ey': ey, 'w': w / 1e6
                })

for fp in board.Footprints():
    for pad in fp.Pads():
        pos = pad.GetPosition()
        px, py = pos.x / 1e6, pos.y / 1e6
        if px > min_x and px < max_x and py > min_y and py < max_y:
            bcu_items.append({
                'type': 'pad',
                'layer': 'all',
                'px': px, 'py': py, 'w': 2.0 # rough estimate
            })

print(f"Found {len(bcu_items)} items in region")

# Check horizontal lines from Y=80 to 95
valid_y_channels = []
for test_y in range(800, 950):
    ty = test_y / 10.0
    
    # We want a horizontal line from x=153 to x=170 at ty
    # Check distance to all items
    collision = False
    for item in bcu_items:
        if item['type'] == 'track':
            # Distance from horizontal line segment to line segment
            # simplified: check if ty is between sy and ey, and sx,ex is in range
            min_iy = min(item['sy'], item['ey']) - item['w']/2 - 0.2
            max_iy = max(item['sy'], item['ey']) + item['w']/2 + 0.2
            
            min_ix = min(item['sx'], item['ex']) - item['w']/2 - 0.2
            max_ix = max(item['sx'], item['ex']) + item['w']/2 + 0.2
            
            if min_iy < ty < max_iy:
                # the track crosses our Y. Does it cross our X?
                if max_ix > 153.0 and min_ix < 170.0:
                    collision = True
                    break
        elif item['type'] == 'pad':
            if abs(item['py'] - ty) < (item['w']/2 + 0.2):
                if item['px'] > 153.0 and item['px'] < 170.0:
                    collision = True
                    break
                    
    if not collision:
        valid_y_channels.append(ty)

print("Valid Y channels for routing:", valid_y_channels)
