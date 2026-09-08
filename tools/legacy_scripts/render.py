import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def parse_step_vertices(filename):
    # This is a very dumb STEP parser that just grabs CARTESIAN_POINTs.
    # It won't capture the geometry perfectly but it gives a cloud of points!
    pts = []
    with open(filename, 'r') as f:
        for line in f:
            if 'CARTESIAN_POINT' in line:
                try:
                    # Example: #123 = CARTESIAN_POINT('',(1.0, 2.0, 3.0));
                    parts = line.split('(')[2].split(')')[0].split(',')
                    pts.append([float(parts[0]), float(parts[1]), float(parts[2])])
                except:
                    pass
    return np.array(pts)

main_pts = parse_step_vertices('build/icio500/icio500_3d_assembly.step')

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
if len(main_pts) > 0:
    # Subsample to avoid huge plots
    step = max(1, len(main_pts)//2000)
    ax.scatter(main_pts[::step,0], main_pts[::step,1], main_pts[::step,2], s=1, alpha=0.5)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.savefig('build/icio500/test_render.png')
print("Render saved to test_render.png with", len(main_pts), "vertices")
