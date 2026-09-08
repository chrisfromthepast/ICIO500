import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

def extract_vertices_from_step(filename):
    points = []
    with open(filename, 'r') as f:
        for line in f:
            if 'CARTESIAN_POINT' in line:
                start = line.find('((')
                if start == -1:
                    start = line.find(',(')
                if start != -1:
                    end = line.find('))', start)
                    if end == -1:
                        end = line.find(')', start + 2)
                    coords = line[start+2:end].split(',')
                    if len(coords) == 3:
                        try:
                            x, y, z = map(float, coords)
                            points.append((x, y, z))
                        except ValueError:
                            pass
    return np.array(points)

# Downsample points for performance
def get_downsampled_points(filename, sample_rate=100):
    pts = extract_vertices_from_step(filename)
    if len(pts) == 0:
        return pts
    return pts[::sample_rate]

print("Loading step files...")
main_pts = get_downsampled_points('build/icio500/icio500_3d_assembly.step', 50)

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

if len(main_pts) > 0:
    ax.scatter(main_pts[:, 0], main_pts[:, 1], main_pts[:, 2], c='b', marker='.', s=1, alpha=0.5)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Set equal aspect ratio
max_range = np.array([main_pts[:, 0].max()-main_pts[:, 0].min(), 
                      main_pts[:, 1].max()-main_pts[:, 1].min(), 
                      main_pts[:, 2].max()-main_pts[:, 2].min()]).max() / 2.0
mid_x = (main_pts[:, 0].max()+main_pts[:, 0].min()) * 0.5
mid_y = (main_pts[:, 1].max()+main_pts[:, 1].min()) * 0.5
mid_z = (main_pts[:, 2].max()+main_pts[:, 2].min()) * 0.5
ax.set_xlim(mid_x - max_range, mid_x + max_range)
ax.set_ylim(mid_y - max_range, mid_y + max_range)
ax.set_zlim(mid_z - max_range, mid_z + max_range)

plt.savefig('build/icio500/assembly_preview.png', dpi=150)
print("Saved preview to assembly_preview.png")
