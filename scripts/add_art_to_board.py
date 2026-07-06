import pcbnew
import sys

def main():
    board_path = 'build/icio500/faceplate_front.kicad_pcb'
    b = pcbnew.LoadBoard(board_path)
    
    # Try to remove old art if it exists
    old_art = b.FindFootprintByReference('ART1')
    if old_art:
        b.RemoveNative(old_art)
        
    # Load the footprint
    fp = pcbnew.FootprintLoad('build/icio500/WispyArt.pretty', 'WispyArt')
    if not fp:
        print("Failed to load footprint")
        sys.exit(1)
        
    fp.SetReference('ART1')
    fp.SetPosition(pcbnew.VECTOR2I(0, 0)) # Position is already offset in the generator
    
    b.Add(fp)
    pcbnew.SaveBoard(board_path, b)
    print("Successfully added WispyArt to the board.")

if __name__ == "__main__":
    main()
