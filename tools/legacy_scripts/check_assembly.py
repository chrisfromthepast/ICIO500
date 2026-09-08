import sys

def get_bounding_box(filename):
    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')
    min_z, max_z = float('inf'), float('-inf')
    
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
                            min_x, max_x = min(min_x, x), max(max_x, x)
                            min_y, max_y = min(min_y, y), max(max_y, y)
                            min_z, max_z = min(min_z, z), max(max_z, z)
                        except ValueError:
                            pass
                            
    return (min_x, max_x), (min_y, max_y), (min_z, max_z)

print("Assembly Bounding Box:")
bbox = get_bounding_box('build/icio500/icio500_3d_assembly.step')
print(f"X: {bbox[0][0]:.2f} to {bbox[0][1]:.2f} (width: {bbox[0][1] - bbox[0][0]:.2f}mm)")
print(f"Y: {bbox[1][0]:.2f} to {bbox[1][1]:.2f} (height: {bbox[1][1] - bbox[1][0]:.2f}mm)")
print(f"Z: {bbox[2][0]:.2f} to {bbox[2][1]:.2f} (depth: {bbox[2][1] - bbox[2][0]:.2f}mm)")
