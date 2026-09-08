import pcbnew
try:
 fp = pcbnew.FootprintLoad('C:/Program Files/KiCad/10.0/share/kicad/footprints/MountingHole.pretty', 'MountingHole_3.2mm_M3')
 print('Loaded:', fp)
except Exception as e:
 print('Error:', e)
