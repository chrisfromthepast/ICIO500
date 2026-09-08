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

main = parse_step_vertices('build/icio500/icio500_3d_assembly.step')
# Find the distinct clusters of points to identify where the boards are
# Main PCB is around X=52 to 203, Y=-169 to -55, Z=0 to 1.6
# Let's filter points to find where the satellite is
# Satellite has a lot of points.
# Let's just print min/max of points where X < 50
left_pts = main[main[:,0] < 50]
if len(left_pts) > 0:
    print("Models at X < 50 (Faceplate/Satellite):")
    print("  X:", np.min(left_pts[:,0]), "to", np.max(left_pts[:,0]))
    print("  Y:", np.min(left_pts[:,1]), "to", np.max(left_pts[:,1]))
    print("  Z:", np.min(left_pts[:,2]), "to", np.max(left_pts[:,2]))
else:
    print("No models at X < 50")
