import cadquery as cq
import os

def load_step(path):
    return cq.importers.importStep(path)

def create_stackup(faceplate_path, logic_path, output_path, z_offset=1.0):
    # Load both STEP models
    fp = load_step(faceplate_path)
    lg = load_step(logic_path)
    # Move logic board down (negative Z) to stack back‑to‑back
    lg = lg.translate((0, 0, -z_offset))
    # Combine the two solids
    combined = fp.union(lg)
    # Export the combined STEP
    cq.exporters.export(combined, output_path)
    print(f"Combined stackup exported to {output_path}")
    # Also export a simple top‑view SVG for a PNG preview
    try:
        svg_path = os.path.splitext(output_path)[0] + ".svg"
        cq.exporters.export(combined, svg_path)
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        drawing = svg2rlg(svg_path)
        png_path = os.path.splitext(output_path)[0] + ".png"
        renderPM.drawToFile(drawing, png_path, fmt='PNG', dpi=300)
        print(f"Preview PNG saved to {png_path}")
    except Exception as e:
        print('Unable to generate PNG preview:', e)

if __name__ == '__main__':
    faceplate_step = 'build/icio500/faceplate_front.step'
    logic_step = 'build/icio500/faceplate_logic.step'
    output_step = 'build/icio500/stackup.step'
    create_stackup(faceplate_step, logic_step, output_step)
