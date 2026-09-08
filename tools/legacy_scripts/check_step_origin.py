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
    return points

pts = extract_vertices_from_step('build/icio500/panel_satellite.step')
xs = [p[0] for p in pts]
ys = [p[1] for p in pts]
zs = [p[2] for p in pts]
print("Satellite STEP center:", (max(xs)+min(xs))/2, (max(ys)+min(ys))/2, (max(zs)+min(zs))/2)
