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
3. **Schematics & Electrical Safety (Strict Rule)**:
    * **NEVER** hand-build IC symbols or embedded `lib_symbols` from memory in Python, **NEVER** reverse-generate `.kicad_sch` files from an existing `.kicad_pcb`, and **NEVER** patch electrical nets in `.kicad_pcb` via scripts.
    * Schematics must originate in KiCad using vetted libraries (or EasyEDA/SnapEDA/manufacturer-PDF-verified symbols) and forward-annotate cleanly into the PCB. Follow all pre-tapeout gates in the workspace `AGENTS.md`.
4. **Rendering**:
    * Render schematics by exporting to SVG using `kicad-cli.exe sch export svg`.
    * Render PCB layouts by exporting SVG via `kicad-cli.exe pcb export svg`.
    * Use Pillow or `svglib` in the system python to assemble side-by-side stackup previews so the user can visualize the results.
