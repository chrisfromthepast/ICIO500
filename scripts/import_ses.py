import pcbnew
import sys

PCB_PATH = 'build/icio500/icio500.kicad_pcb'
SES_PATH = 'build/icio500/icio500.ses'

try:
    b = pcbnew.LoadBoard(PCB_PATH)
    pcbnew.ImportSpecctraSES(b, SES_PATH)
    
    b.BuildConnectivity()
    pcbnew.SaveBoard(PCB_PATH, b)
    print(f'Successfully imported {SES_PATH} and saved to {PCB_PATH}')
except Exception as e:
    print('Error:', e)
