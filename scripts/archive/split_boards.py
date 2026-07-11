import pcbnew
import shutil
import os

def main():
    # 0. Load old boards to grab their shapes
    old_logic = pcbnew.LoadBoard('build/icio500/faceplate_logic.kicad_pcb')
    old_front = pcbnew.LoadBoard('build/icio500/faceplate_front.kicad_pcb')
    
    logic_shapes = [s for s in old_logic.GetDrawings() if s.GetLayer() == pcbnew.Edge_Cuts or s.GetLayer() == pcbnew.F_SilkS or s.GetLayer() == pcbnew.B_SilkS]
    front_shapes = [s for s in old_front.GetDrawings() if s.GetLayer() == pcbnew.Edge_Cuts or s.GetLayer() == pcbnew.F_SilkS or s.GetLayer() == pcbnew.B_SilkS]

    # 1. Copy the built board to logic and front
    shutil.copy('build/icio500/icio500.kicad_pcb', 'build/icio500/faceplate_logic.kicad_pcb')
    shutil.copy('build/icio500/icio500.kicad_pcb', 'build/icio500/faceplate_front.kicad_pcb')
    
    # 2. Logic Board
    logic = pcbnew.LoadBoard('build/icio500/faceplate_logic.kicad_pcb')
    # Remove all drawings from logic board (since they are from the mainboard)
    for dwg in list(logic.GetDrawings()):
        logic.RemoveNative(dwg)
    # Add old shapes
    for s in logic_shapes:
        new_s = s.Duplicate()
        logic.Add(new_s)
        
    for fp in list(logic.GetFootprints()):
        path = fp.GetPath().AsString()
        ref = fp.GetReference()
        if 'header_panel' in path or ref == 'header_panel':
            logic.RemoveNative(fp)
        if ref == 'ART1':
            logic.RemoveNative(fp)
    pcbnew.SaveBoard('build/icio500/faceplate_logic.kicad_pcb', logic)
    
    # 3. Front Board
    front = pcbnew.LoadBoard('build/icio500/faceplate_front.kicad_pcb')
    for dwg in list(front.GetDrawings()):
        front.RemoveNative(dwg)
    for s in front_shapes:
        new_s = s.Duplicate()
        front.Add(new_s)
        
    for fp in list(front.GetFootprints()):
        path = fp.GetPath().AsString()
        ref = fp.GetReference()
        keep = False
        if 'header_panel' in path or ref == 'header_panel':
            keep = True
        if ref == 'ART1':
            keep = True
        if not keep:
            front.RemoveNative(fp)
    pcbnew.SaveBoard('build/icio500/faceplate_front.kicad_pcb', front)
    print("Successfully split boards and retained edge cuts!")

if __name__ == "__main__":
    main()
