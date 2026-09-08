import math
def rx(ang, v):
    a = math.radians(ang)
    x, y, z = v
    return (x, y*math.cos(a) - z*math.sin(a), y*math.sin(a) + z*math.cos(a))
def ry(ang, v):
    a = math.radians(ang)
    x, y, z = v
    return (x*math.cos(a) + z*math.sin(a), y, -x*math.sin(a) + z*math.cos(a))
def rz(ang, v):
    a = math.radians(ang)
    x, y, z = v
    return (x*math.cos(a) - y*math.sin(a), x*math.sin(a) + y*math.cos(a), z)

angles = [0, 90, 180, -90]
for z in angles:
    for y in angles:
        for x in angles:
            v = (1, 2, 3) # x, y, z
            # KiCad applies X, then Y, then Z? Or Z, Y, X?
            # Let's test KiCad's standard Z-Y-X rotation
            v1 = rz(z, ry(y, rx(x, v)))
            v_target = (-3, 1, -2) # (-z, x, -y)
            
            # rounding
            v1 = (round(v1[0]), round(v1[1]), round(v1[2]))
            if v1 == v_target:
                print(f"XYZ Order: Rx={x}, Ry={y}, Rz={z}")
            
            v2 = rx(x, ry(y, rz(z, v)))
            v2 = (round(v2[0]), round(v2[1]), round(v2[2]))
            if v2 == v_target:
                print(f"ZYX Order: Rx={x}, Ry={y}, Rz={z}")

