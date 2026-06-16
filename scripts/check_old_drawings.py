import pcbnew
import subprocess

subprocess.run(['git', 'show', 'dfb5c8d:build/icio500/icio500.kicad_pcb'], stdout=open('commit_dfb5c8d.kicad_pcb', 'w'))
subprocess.run(['git', 'show', 'f17cf5f:build/icio500/icio500.kicad_pcb'], stdout=open('commit_f17cf5f.kicad_pcb', 'w'))

def list_drawings(filename):
    print(f"--- {filename} ---")
    try:
        b = pcbnew.LoadBoard(filename)
    except:
        print("Failed to load")
        return
        
    for d in b.GetDrawings():
        layer = b.GetLayerName(d.GetLayer())
        if "User" in layer or "Cuts" in layer or "Silk" in layer or "Fab" in layer:
            if type(d) is pcbnew.PCB_TEXT:
                print(f"[{layer}] TEXT: {d.GetText()}")
            elif type(d) is pcbnew.PCB_SHAPE:
                shape_type = getattr(d, 'GetShapeStr', lambda: 'Unknown')()
                print(f"[{layer}] SHAPE: {shape_type} at {d.GetStart().x/1e6},{d.GetStart().y/1e6} to {d.GetEnd().x/1e6},{d.GetEnd().y/1e6}")
            else:
                print(f"[{layer}] OTHER: {type(d)}")

list_drawings('commit_dfb5c8d.kicad_pcb')
list_drawings('commit_f17cf5f.kicad_pcb')
