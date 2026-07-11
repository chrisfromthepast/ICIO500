import pcbnew
import sys
import math

def main():
    source_board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
    logic_board = pcbnew.LoadBoard('build/icio500/faceplate_logic.kicad_pcb')
    front_board = pcbnew.LoadBoard('build/icio500/faceplate_front.kicad_pcb')

    # The Front Board gets header_panel
    # The Logic Board gets everything else from Faceplate

    # Step 1: Copy footprints from source to logic if they don't exist, and update nets
    # Since it's easier, we'll just clear the logic board's old components and recreate them?
    # No, keep positions of existing ones!
    
    # Let's map existing logic board components by reference
    logic_fps = {fp.GetReference(): fp for fp in logic_board.GetFootprints()}
    front_fps = {fp.GetReference(): fp for fp in front_board.GetFootprints()}

    for fp in source_board.GetFootprints():
        ref = fp.GetReference()
        path = fp.GetPath().AsString()
        
        # We only care about Faceplate components
        if not path.startswith('/faceplate'):
            continue
            
        # If it belongs on front board:
        if 'header_panel' in path:
            # Sync to front board
            if ref in front_fps:
                pass # Just keep it
            else:
                # Add to front board
                new_fp = pcbnew.Cast_to_FOOTPRINT(fp.Duplicate())
                front_board.Add(new_fp)
                new_fp.SetPosition(pcbnew.VECTOR2I(int(29.05*1e6), int(90.5*1e6)))
                new_fp.SetLayer(pcbnew.B_Cu)
            continue
            
        # Everything else belongs on Logic Board!
        if ref in logic_fps:
            # Update nets or footprint if needed?
            # It's safer to just replace the footprint to get the new nets
            old_fp = logic_fps[ref]
            pos = old_fp.GetPosition()
            rot = old_fp.GetOrientation()
            layer = old_fp.GetLayer()
            
            logic_board.RemoveNative(old_fp)
            
            new_fp = pcbnew.Cast_to_FOOTPRINT(fp.Duplicate())
            logic_board.Add(new_fp)
            new_fp.SetPosition(pos)
            new_fp.SetOrientation(rot)
            new_fp.SetLayer(layer)
        else:
            # New footprint! (e.g. 10 LEDs, driver)
            new_fp = pcbnew.Cast_to_FOOTPRINT(fp.Duplicate())
            logic_board.Add(new_fp)
            # Default placement off to the side so we can arrange them later
            new_fp.SetPosition(pcbnew.VECTOR2I(int(5*1e6), int(5*1e6)))
            
    # Now, let's remove old footprints from logic board that no longer exist in source
    source_refs = [f.GetReference() for f in source_board.GetFootprints() if f.GetPath().AsString().startswith('/faceplate')]
    for ref, fp in list(logic_fps.items()):
        if ref not in source_refs and ref != 'DUMMY':
            logic_board.RemoveNative(fp)
            
    # Same for front board (remove U4, C3, etc)
    for ref, fp in list(front_fps.items()):
        if ref not in source_refs and ref not in ['ART1']:
            front_board.RemoveNative(fp)

    pcbnew.SaveBoard('build/icio500/faceplate_logic.kicad_pcb', logic_board)
    pcbnew.SaveBoard('build/icio500/faceplate_front.kicad_pcb', front_board)
    print("Successfully synced logic and front boards from source netlist!")

if __name__ == "__main__":
    main()
