from scipy.spatial.transform import Rotation as R
import numpy as np

# We want original faceplate (x, y, z) to map to board (X, Y, Z).
# X_board points right (width of module).
# Y_board points down (length of module).
# Z_board points UP out of the board.

# Original faceplate:
# +x points right (width).
# +y points down (height).
# +z points UP (thickness, out of front panel).

# When mounted at the front (Y is length, so front is -Y... wait. The board edge connector is at +X (X=203), front is at X=52.17.
# So length of module is along X axis!
# Faceplate front surface should point towards -X!
# So faceplate +z (out of front) -> -X_board.
# Faceplate +x (right side) -> +Y_board (since board Y goes from 55 to 169.
# Faceplate +y (down) -> -Z_board (since board Z points UP).

# Target mapping:
# (x, y, z) -> (-z, x, -y)
target_matrix = np.array([
    [ 0,  0, -1],
    [ 1,  0,  0],
    [ 0, -1,  0]
])

r = R.from_matrix(target_matrix)
# KiCad applies Z, then Y, then X. Extrinsic or intrinsic? Usually extrinsic XYZ or intrinsic zyx.
# Let's get Euler angles for 'xyz' and 'ZYX'.
euler = r.as_euler('xyz', degrees=True)
print('KiCad rotation (xyz):', euler)

# Check inverse mapping just to be sure.
