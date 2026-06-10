import pcbnew
import os

pcb_path = os.path.join("build", "icio500", "icio500.kicad_pcb")
board = pcbnew.LoadBoard(pcb_path)

print("Edge.Cuts Geometry:")
for d in board.GetDrawings():
    if d.GetLayer() == pcbnew.Edge_Cuts:
        if isinstance(d, pcbnew.PCB_SHAPE):
            shape_type = d.GetShape()
            # 0: Segment, 1: Rect, 2: Arc, 3: Circle, 4: Polygon, 5: Curve
            if shape_type == pcbnew.SHAPE_T_SEGMENT:
                print(f"Segment: ({d.GetStart().x/1e6:.2f}, {d.GetStart().y/1e6:.2f}) to ({d.GetEnd().x/1e6:.2f}, {d.GetEnd().y/1e6:.2f})")
            elif shape_type == pcbnew.SHAPE_T_ARC:
                print(f"Arc: Center ({d.GetCenter().x/1e6:.2f}, {d.GetCenter().y/1e6:.2f}), Radius {d.GetRadius()/1e6:.2f}")
            else:
                print(f"Other shape: {shape_type}")
