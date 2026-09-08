import sys

def get_bounding_box(filename):
    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')
    min_z, max_z = float('inf'), float('-inf')
    
    with open(filename, 'r') as f:
        for line in f:
            if 'CARTESIAN_POINT' in line:
                # Format is usually: #123 = CARTESIAN_POINT('', (x, y, z));
                # Let's extract the coordinates
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

print(get_bounding_box('build/icio500/panel_satellite.step'))
