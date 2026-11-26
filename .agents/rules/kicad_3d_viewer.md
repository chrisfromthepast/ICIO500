---
description: Definitive guide to KiCad mechanical assemblies, STEP exports, and 3D Viewer offset math.
---

# KiCad 3D Assembly & Mechanical Alignment Rules

When building mechanical assemblies of multiple PCBs in KiCad, you will encounter several deeply non-intuitive quirks in KiCad 10. **Read and apply these rules strictly to avoid floating boards, inverted axes, and mismatched renders.**

## 1. The STEP Export Origin Trap (The cause of all divergence)

**The Bug:** By default, `kicad-cli pcb export step` centers the exported 3D model around its *bounding box*, NOT the `(0,0)` coordinate of the PCB canvas. Because bounding boxes change wildly based on edge connectors or off-board text, the STEP file's internal origin becomes unpredictable, and causes the GUI 3D Viewer and the CLI renderer to interpret the origin differently.
**The Fix:** ALWAYS export child STEP files with an explicit zero origin:
`kicad-cli pcb export step child_board.kicad_pcb --user-origin 0x0in`
This forces the STEP file's `(0,0,0)` to exactly match the PCB's `(0,0)` canvas coordinate.

## 2. Coordinate Mapping & The Y-Axis Inversion

- **PCB Canvas:** Y increases **DOWNWARDS**.
- **3D Viewer / STEP:** Y increases **UPWARDS**.
When a board is exported to STEP, its Y coordinates are mathematically negated. (e.g., A component at `Y = 175` on the PCB canvas becomes `Y = -175` in the STEP file).

## 3. Rotation Matrices (Right-Handed)

KiCad's 3D Viewer uses a strict Right-Handed coordinate system (`+X` is Right, `+Y` is Up, `+Z` is Towards Viewer). When rotating a child board (like a faceplate) to sit perpendicularly:

- **Ry = -90 (Faces FRONT):**
  `X_new = Z`
  `Y_new = Y`
  `Z_new = -X`
  *(Use this for front faceplates and daughtercards where `F.Cu` must face the user/front).*

## 4. The Transformation Order (Offset BEFORE Rotation)

**BOTH the KiCad GUI 3D Viewer and the `kicad-cli pcb render` tool apply the XYZ Offset BEFORE the Rotation.**
Because the offset is applied *before* the rotation, the XYZ offsets you provide in the `.kicad_pcb` file MUST be calculated in the **RAW UNROTATED COORDINATE SPACE** of the child board!

### How to Calculate Perfect Offsets:
Assuming you exported the STEP with `--user-origin 0x0in`:
1. Identify the absolute center `(X, Y, Z)` of the child board in the PCB canvas.
2. Remember that in the STEP file, this is `(X, -Y, Z)`.
3. Do NOT apply your rotation matrix yet!
4. Calculate the raw offsets needed to shift `(X, -Y, Z)` to exactly `(0, 0, 0)`.
5. Enter these UNROTATED offsets directly into the `.kicad_pcb` file's offset block.
6. The GUI will naturally shift the board to `(0,0,0)` and *then* apply your rotation, placing it perfectly on the Dummy footprint's absolute location.

## 5. Assembly File Synchronization

If you build an assembly file (`_assembly.kicad_pcb`) by copying the main board and adding DUMMY footprints to hold the child 3D models:
**Rule:** If you move footprints, change connectors, or re-route traces on the main board, you **MUST** sync those changes to the assembly file (e.g., by copying the main board over again and re-injecting the DUMMY footprints). Otherwise, you will align the 3D models to phantom positions that no longer exist, leading to massive confusion about alignment.
