import pcbnew
import sys

board = pcbnew.GetBoard()
# just a quick script to see if we can load the footprint
try:
    fp = pcbnew.FootprintLoad('Connector_PinHeader_2.54mm', 'PinHeader_2x10_P2.54mm_Vertical_SMD')
    if fp:
        print("Found SMD footprint!")
    else:
        print("Not found.")
except Exception as e:
    print("Error:", e)
