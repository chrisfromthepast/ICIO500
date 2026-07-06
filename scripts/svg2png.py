import sys
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

if len(sys.argv) != 3:
    print("Usage: svg2png.py <in.svg> <out.png>")
    sys.exit(1)

drawing = svg2rlg(sys.argv[1])
renderPM.drawToFile(drawing, sys.argv[2], fmt='PNG')
print(f"Rendered {sys.argv[2]}")
