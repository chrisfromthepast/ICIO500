import math
def rotate(x, y, z):
    return (
        round(x*math.cos(math.radians(z)) - y*math.sin(math.radians(z))),
        round(x*math.sin(math.radians(z)) + y*math.cos(math.radians(z))),
        z
    )

def rx(ang, v):
    a = math.radians(ang)
    x, y, z = v
    return (x, round(y*math.cos(a) - z*math.sin(a)), round(y*math.sin(a) + z*math.cos(a)))

def ry(ang, v):
    a = math.radians(ang)
    x, y, z = v
    return (round(x*math.cos(a) + z*math.sin(a)), y, round(-x*math.sin(a) + z*math.cos(a)))

def rz(ang, v):
    a = math.radians(ang)
    x, y, z = v
    return (round(x*math.cos(a) - y*math.sin(a)), round(x*math.sin(a) + y*math.cos(a)), z)

angles = [0, 90, 180, -90]
target = (3, 1, -2) # z, x, -y  for v=(1,2,3)
for x in angles:
    for y in angles:
        for z in angles:
            v = (1, 2, 3)
            # KiCad applies X, then Y, then Z or vice versa?
            # Let's check extrinsic Z, Y, X
            v1 = rx(x, ry(y, rz(z, v)))
            if v1 == target:
                print(f"Extrinsic ZYX (KiCad standard): Rx={x}, Ry={y}, Rz={z}")
            # Let's check extrinsic X, Y, Z
            v2 = rz(z, ry(y, rx(x, v)))
            if v2 == target:
                print(f"Extrinsic XYZ: Rx={x}, Ry={y}, Rz={z}")

