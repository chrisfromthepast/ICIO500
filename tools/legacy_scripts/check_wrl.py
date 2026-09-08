def check_wrl(filename):
    pts = []
    with open(filename, 'r') as f:
        for line in f:
            if ',' in line and not line.strip().startswith('#'):
                parts = line.strip().replace(',', ' ').split()
                if len(parts) == 3:
                    try:
                        pts.append([float(parts[0]), float(parts[1]), float(parts[2])])
                    except:
                        pass
    if len(pts) > 0:
        pts = sorted(pts, key=lambda p: p[1])
        min_y = pts[0][1]
        max_y = pts[-1][1]
        print(f"Y bounds: {min_y} to {max_y}")
    else:
        print("No points")

check_wrl('build/icio500/faceplate_front.wrl')
