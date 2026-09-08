from scipy.spatial.transform import Rotation as R
import numpy as np

# Point
p = [119.05, -166.675, 0.8]

# Ry = -90 (intrinsic? extrinsic?)
# Let's assume standard right-hand rule
r = R.from_euler('y', -90, degrees=True)
p_rot = r.apply(p)
print(f"Ry=-90 applied to {p}: {p_rot}")
