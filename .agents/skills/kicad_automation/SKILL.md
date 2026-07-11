---
name: KiCad Python Automation
description: Guidelines and tools for automating KiCad PCB and Schematic tasks.
---

# KiCad Python Automation

When asked to generate or edit KiCad schematics and PCBs, use the following approach:

1. **Procedural Generation**: Use Python scripts leveraging the KiCad API (`pcbnew`) to programmatically generate boards and components. 
2. **Defensive API usage**: Be aware that `pcbnew` objects can cause segfaults or access violations if not handled correctly.
    * For placing components and drawing board outlines, python is safe.
    * DO NOT use `pcbnew` for drawing tracks, rendering zones, or zone filling via automated scripts because it frequently causes memory management conflicts between Python and C++ that result in a hard crash (`0xC0000005`).
    * Let the user route traces manually in the GUI.
3. **Schematic Generation**: Use custom string-building python scripts to generate `.kicad_sch` files with built-in embedded libraries (`lib_symbols`) so the user doesn't have to resolve missing library references.
4. **Rendering**:
    * Render schematics by exporting to SVG using `kicad-cli.exe sch export svg`.
    * Render PCB layouts by exporting SVG via `kicad-cli.exe pcb export svg`.
    * Use Pillow or `svglib` in the system python to assemble side-by-side stackup previews so the user can visualize the results.
