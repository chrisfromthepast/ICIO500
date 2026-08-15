import sys
print("Script started", flush=True)
try:
    import pcbnew
    print(f"pcbnew loaded, version: {pcbnew.Version()}", flush=True)
    
    PCB_PATH = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\build\icio500\icio500.kicad_pcb"
    print(f"Loading board: {PCB_PATH}", flush=True)
    board = pcbnew.LoadBoard(PCB_PATH)
    print("Board loaded OK", flush=True)
    
    edge_cuts_layer = board.GetLayerID("Edge.Cuts")
    print(f"Edge.Cuts layer ID: {edge_cuts_layer}", flush=True)
    
    count = 0
    for d in board.GetDrawings():
        if d.GetLayer() == edge_cuts_layer:
            count += 1
    print(f"Found {count} Edge.Cuts drawings", flush=True)
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}", flush=True)
    sys.exit(1)
