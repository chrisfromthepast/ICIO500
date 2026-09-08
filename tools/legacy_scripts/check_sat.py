import numpy as np
def parse_step_vertices(filename):
    pts = []
    with open(filename, 'r') as f:
        for line in f:
            if 'CARTESIAN_POINT' in line:
                try:
                    parts = line.split('(')[2].split(')')[0].split(',')
                    pts.append([float(parts[0]), float(parts[1]), float(parts[2])])
                except:
                    pass
    return np.array(pts)

sat_pts = parse_step_vertices('build/icio500/panel_satellite.step')
if len(sat_pts) > 0:
    min_pt = np.min(sat_pts, axis=0)
    max_pt = np.max(sat_pts, axis=0)
    print("Satellite Bounding box:")
    print("X:", min_pt[0], "to", max_pt[0])
    print("Y:", min_pt[1], "to", max_pt[1])
    print("Z:", min_pt[2], "to", max_pt[2])
else:
    print("No vertices found")
