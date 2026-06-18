import pcbnew
import math

b = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

# 1. Delete all existing user-drawn graphical lines on F.SilkS and F.Fab
for d in list(b.GetDrawings()):
    if d.GetLayer() in [pcbnew.F_SilkS, pcbnew.F_Fab] and isinstance(d, pcbnew.PCB_SHAPE):
        if d.GetShape() in [pcbnew.SHAPE_T_SEGMENT, pcbnew.SHAPE_T_RECT]:
            b.Remove(d)

# 2. Group EVERY footprint on the board into one of the clusters based on coordinates
# Digital: x < 100
# Scaling: 100 <= x < 140, y < 50
# Line Driver: x >= 140, y < 60
# Balanced Input: 120 <= x < 155, 60 <= y < 90
# Power: 120 <= x, y >= 90
clusters = {
    'DIGITAL PROCESSING': [],
    'SCALING': [],
    'LINE DRIVER': [],
    'BALANCED INPUT': [],
    'POWER': []
}

for fp in b.GetFootprints():
    ref = fp.GetReference()
    pos = fp.GetPosition()
    x = pos.x / 1e6
    y = pos.y / 1e6
    
    if x < 100:
        clusters['DIGITAL PROCESSING'].append(fp)
    elif y < 55 and x < 135:
        clusters['SCALING'].append(fp)
    elif y < 55 and x >= 135:
        clusters['LINE DRIVER'].append(fp)
    elif y >= 55 and y < 95 and x > 100:
        clusters['BALANCED INPUT'].append(fp)
    elif y >= 95 and x > 100:
        clusters['POWER'].append(fp)

# 3. Find the exact bounding box of the footprints in each cluster
cluster_bounds = {}
for name, fps in clusters.items():
    if not fps:
        continue
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = float('-inf'), float('-inf')
    for fp in fps:
        bb = fp.GetBoundingBox()
        min_x = min(min_x, bb.GetX())
        min_y = min(min_y, bb.GetY())
        max_x = max(max_x, bb.GetRight())
        max_y = max(max_y, bb.GetBottom())
    if min_x != float('inf'):
        cluster_bounds[name] = [min_x, min_y, max_x, max_y]

MM = 1e6
margin = 2.0 * MM

boxes = {}
for name, bounds in cluster_bounds.items():
    boxes[name] = [bounds[0] - margin, bounds[1] - margin, bounds[2] + margin, bounds[3] + margin]

# Fix overlaps:
if 'DIGITAL PROCESSING' in boxes and 'BALANCED INPUT' in boxes:
    dp = boxes['DIGITAL PROCESSING']
    bi = boxes['BALANCED INPUT']
    if dp[2] > bi[0] - 1*MM:
        midpoint = (dp[2] + bi[0]) / 2
        dp[2] = midpoint - 0.5*MM
        bi[0] = midpoint + 0.5*MM

if 'DIGITAL PROCESSING' in boxes and 'POWER' in boxes:
    dp = boxes['DIGITAL PROCESSING']
    pw = boxes['POWER']
    if dp[2] > pw[0] - 1*MM:
        midpoint = (dp[2] + pw[0]) / 2
        dp[2] = midpoint - 0.5*MM
        pw[0] = midpoint + 0.5*MM

if 'SCALING' in boxes and 'DIGITAL PROCESSING' in boxes:
    sc = boxes['SCALING']
    dp = boxes['DIGITAL PROCESSING']
    if sc[3] > dp[1] - 1*MM:
        if sc[0] < dp[2]: # only if x overlaps
            midpoint = (sc[3] + dp[1]) / 2
            sc[3] = midpoint - 0.5*MM
            dp[1] = midpoint + 0.5*MM

if 'SCALING' in boxes and 'LINE DRIVER' in boxes:
    sc = boxes['SCALING']
    ld = boxes['LINE DRIVER']
    if sc[2] > ld[0] - 1*MM:
        midpoint = (sc[2] + ld[0]) / 2
        sc[2] = midpoint - 0.5*MM
        ld[0] = midpoint + 0.5*MM

if 'LINE DRIVER' in boxes and 'BALANCED INPUT' in boxes:
    ld = boxes['LINE DRIVER']
    bi = boxes['BALANCED INPUT']
    if ld[3] > bi[1] - 1*MM:
        midpoint = (ld[3] + bi[1]) / 2
        ld[3] = midpoint - 0.5*MM
        bi[1] = midpoint + 0.5*MM

if 'BALANCED INPUT' in boxes and 'POWER' in boxes:
    bi = boxes['BALANCED INPUT']
    pw = boxes['POWER']
    if bi[3] > pw[1] - 1*MM:
        midpoint = (bi[3] + pw[1]) / 2
        bi[3] = midpoint - 0.5*MM
        pw[1] = midpoint + 0.5*MM

def draw_rect(board, min_x, min_y, max_x, max_y, layer):
    lines = [
        (min_x, min_y, max_x, min_y),
        (max_x, min_y, max_x, max_y),
        (max_x, max_y, min_x, max_y),
        (min_x, max_y, min_x, min_y)
    ]
    for x1, y1, x2, y2 in lines:
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(layer)
        seg.SetStart(pcbnew.VECTOR2I(int(x1), int(y1)))
        seg.SetEnd(pcbnew.VECTOR2I(int(x2), int(y2)))
        seg.SetWidth(int(0.15 * MM))
        board.Add(seg)

for name, rect in boxes.items():
    draw_rect(b, rect[0], rect[1], rect[2], rect[3], pcbnew.F_SilkS)

# Move labels:
# Also delete any other F.SilkS text that we don't care about, or move the label names
# Actually the user has specific label names.
for d in b.GetDrawings():
    if isinstance(d, pcbnew.PCB_TEXT) and d.GetLayer() == pcbnew.F_SilkS:
        text = d.GetText()
        if text in boxes:
            rect = boxes[text]
            d.SetPosition(pcbnew.VECTOR2I(int(rect[0] + 1*MM), int(rect[1] - 1*MM)))

pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', b)
print('Boxes fixed!')
