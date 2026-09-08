import math

def rot_y(x, y, z, deg):
    rad = math.radians(deg)
    # Right-hand rule rotation around Y
    # X_new = X*cos(a) + Z*sin(a)
    # Y_new = Y
    # Z_new = -X*sin(a) + Z*cos(a)
    nx = x * math.cos(rad) + z * math.sin(rad)
    ny = y
    nz = -x * math.sin(rad) + z * math.cos(rad)
    return (nx, ny, nz)

print("-90: ", rot_y(119.05, -166.675, 0.8, -90))
print("+90: ", rot_y(119.05, -166.675, 0.8, 90))
