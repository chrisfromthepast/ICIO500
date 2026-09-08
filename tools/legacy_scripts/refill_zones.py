import sys
try:
    import pcbnew
except ImportError:
    print("Failed to import pcbnew")
    sys.exit(1)

print("Loading PCB...")
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

print("Refilling zones...")
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

print("Saving PCB...")
pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
print("Done!")
