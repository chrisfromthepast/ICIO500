import pcbnew
import sys

def main():
    board = pcbnew.LoadBoard('build/icio500/faceplate_front.kicad_pcb')
    
    # Remove old "dinky" graphics around the encoder (Y=15 to Y=37)
    for dwg in list(board.GetDrawings()):
        if isinstance(dwg, pcbnew.PCB_SHAPE):
            layer = dwg.GetLayerName()
            if layer in ['F.Cu', 'F.Mask']:
                bbox = dwg.GetBoundingBox()
                c_y = bbox.GetCenter().y / 1e6
                if 15.0 <= c_y <= 37.0:
                    board.RemoveNative(dwg)
                    
    # Inject the new EncoderGraphic footprint
    try:
        fp = pcbnew.FootprintLoad('build/icio500/custom.pretty', 'EncoderGraphic')
    except Exception as e:
        print("Error loading footprint:", e)
        # Try loading directly via LoadBoard if it's a standalone .kicad_mod
        # Wait, FootprintLoad works with directories.
        # .kicad_mod is a single file. Wait, in KiCad, FootprintLoad takes (library_path, footprint_name).
        # We can just put it in a .pretty folder!
        sys.exit(1)
        
    board.Add(fp)
    fp.SetPosition(pcbnew.VECTOR2I(int(19.05 * 1e6), int(24.0 * 1e6)))
    fp.SetLayer(pcbnew.F_Cu)
    
    pcbnew.SaveBoard('build/icio500/faceplate_front.kicad_pcb', board)
    print("Successfully replaced encoder graphics!")

if __name__ == '__main__':
    main()
