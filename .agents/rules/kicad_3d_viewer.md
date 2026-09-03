---
description: Critical rules for modifying KiCad 3D viewer offsets in assemblies.
---

# KiCad 3D Viewer Offset Rules

When writing scripts or manually editing .kicad_pcb files to align 3D models (such as .step files of other PCBs) in a 3D assembly, you **MUST** account for a known bug/discrepancy in how KiCad 10 handles 3D model transformations.

## The Transformation Order Bug

KiCad applies 3D model transformations (Scale, Rotation, Offset) in different orders depending on the tool:
1. **kicad-cli pcb export step**: Applies XYZ offset **BEFORE** otate.
2. **KiCad GUI 3D Viewer**: Applies XYZ offset **AFTER** otate.

**CRITICAL RULE:** Because the user views assemblies in the GUI 3D Viewer, you **MUST calculate your offsets for the GUI 3D Viewer**. Do **NOT** use kicad-cli pcb export step to verify your bounding boxes, because the CLI will output a fundamentally different alignment than what the user sees on their screen.

## How to Calculate Offsets for the GUI 3D Viewer

In the GUI, because the offset is applied **after** the otate, the offsets must be provided in the *rotated coordinate space*.

1. **Absolute Coordinates**: By default, KiCad does NOT auto-center .step files that are loaded via footprints. The .step file retains the raw absolute coordinates of the board from when it was drawn on the grid.
2. **Transformation Math**: 
   To perfectly align a 3D model onto a footprint at (Footprint_X, Footprint_Y), follow this math:
   
   - Let (Model_X, Model_Y, Model_Z) be the absolute center coordinates of the board in the STEP file.
   - Apply your intended Rotation matrix to (Model_X, Model_Y, Model_Z) to get (Rot_X, Rot_Y, Rot_Z).
   - Calculate the offsets needed to shift (Rot_X, Rot_Y, Rot_Z) to (0, 0, 0).
   - Apply those offsets to the xyz offset field in the .kicad_pcb file.
   - The model will now be perfectly centered at (0,0,0) relative to the footprint, and will render exactly at (Footprint_X, Footprint_Y) in the PCB's coordinate space.

**WARNING:** If you attempt to use intuitive offsets (e.g., applying an X offset before an Ry rotation), your models will be flung hundreds of millimeters into outer space in the 3D Viewer. Always map the absolute 2D PCB coordinates of the boards through the rotation matrix FIRST, and then calculate the final offset.
