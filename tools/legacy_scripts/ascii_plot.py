import numpy as np

def parse_step(filename):
    pts = []
    with open(filename, 'r') as f:
        for line in f:
            if 'CARTESIAN_POINT' in line:
                try:
                    parts = line.split('(')[2].split(')')[0].split(',')
                    pts.append([float(parts[0]), float(parts[1]), float(parts[2])])
                except:
                    pass
    return np.array(pts)

main = parse_step('build/icio500/icio500_3d_assembly.step')

def plot_ascii(pts, axis1, axis2, label1, label2, bins=60):
    if len(pts) == 0:
        return
    min1, max1 = np.min(pts[:, axis1]), np.max(pts[:, axis1])
    min2, max2 = np.min(pts[:, axis2]), np.max(pts[:, axis2])
    
    # Expand bounds slightly
    range1 = max1 - min1
    range2 = max2 - min2
    if range1 == 0: range1 = 1
    if range2 == 0: range2 = 1
    
    grid = np.zeros((bins, bins))
    
    for p in pts:
        i = int((p[axis1] - min1) / range1 * (bins - 1))
        j = int((p[axis2] - min2) / range2 * (bins - 1))
        grid[j, i] += 1
        
    print(f"\n--- {label1} vs {label2} ---")
    print(f"{label1}: {min1:.1f} to {max1:.1f}")
    print(f"{label2}: {min2:.1f} to {max2:.1f}")
    
    chars = " .:-=+*#%@"
    for j in range(bins-1, -1, -1):
        row = ""
        for i in range(bins):
            val = grid[j, i]
            idx = int(val / np.max(grid) * 9) if np.max(grid) > 0 else 0
            if val > 0 and idx == 0: idx = 1
            row += chars[idx]
        print(row)

# The coordinates in the STEP file are:
# X: Length of module (front to back)
# Y: Height of module (because KiCad STEP flips Y, this is -169 to -55)
# Z: Width/Thickness of module (0 to 38)
plot_ascii(main, 0, 1, 'X', 'Y', bins=40)
plot_ascii(main, 0, 2, 'X', 'Z', bins=40)

