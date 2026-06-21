import pcbnew
import zipfile
import tempfile
import os

backup_zip = r'C:\Users\Chris Williams\Documents\GitHub\ICIO500\build\icio500\icio500-backups\icio500-2026-06-21_172705.zip'
board_path = r'C:\Users\Chris Williams\Documents\GitHub\ICIO500\build\icio500\icio500.kicad_pcb'

with tempfile.TemporaryDirectory() as td:
    with zipfile.ZipFile(backup_zip, 'r') as zf:
        zf.extractall(td)
    
    backup_pcb_path = os.path.join(td, 'icio500.kicad_pcb')
    backup_board = pcbnew.LoadBoard(backup_pcb_path)
    board = pcbnew.LoadBoard(board_path)
    
    for drawing in backup_board.GetDrawings():
        if drawing.GetLayerName() in ('Edge.Cuts', 'Margin', 'User.Drawings', 'User.Comments'):
            board.Add(drawing.Duplicate())
            
    for fp in backup_board.GetFootprints():
        ref = fp.GetReference()
        if "EDA_306" in fp.GetFPIDAsString() or ref.startswith("G") or not ref:
            board.Add(fp.Duplicate(False))
            
    pcbnew.SaveBoard(board_path, board)
    print("Successfully restored Edge.Cuts and template footprints!")
