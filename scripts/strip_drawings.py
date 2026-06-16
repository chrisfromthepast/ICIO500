"""
Strip all board-level gr_text, gr_line, gr_rect, gr_poly, gr_arc items
that are NOT on the Edge.Cuts layer, by parsing the kicad_pcb as text.
Edge.Cuts items and footprint-internal graphics are left untouched.
"""

import re

PCB_PATH = 'build/icio500/icio500.kicad_pcb'

with open(PCB_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# We only want to remove TOP-LEVEL drawing items (not inside footprints).
# A top-level drawing item starts at column 0 (or 2 spaces indent) and is one of:
# (gr_text ...) (gr_line ...) (gr_rect ...) (gr_poly ...) (gr_arc ...) (gr_circle ...) (dimension ...)
# We need to check that the layer is NOT Edge.Cuts

def remove_non_edge_drawings(text):
    """Parse and remove top-level gr_* items that aren't on Edge.Cuts."""
    result = []
    i = 0
    n = len(text)
    removed = 0
    
    while i < n:
        # Look for top-level drawing items (at start of line with 2 spaces indent)
        # Pattern: starts with \n  (gr_text or gr_line or gr_rect etc
        match = re.match(
            r'(\s*\((gr_text|gr_line|gr_rect|gr_poly|gr_arc|gr_circle|dimension)(\s|\())',
            text[i:],
            re.DOTALL
        )
        
        if match and text[i:i+2] in ('  ', '\t\t') or (i == 0 and text[i] == '('):
            # Check if this is truly top-level (not inside a footprint)
            # Count parens before this position to determine depth
            depth = text[:i].count('(') - text[:i].count(')')
            
            if depth <= 1:  # Top-level (depth 0 = file root, 1 = inside kicad_pcb)
                m = re.match(r'\s*\(', text[i:])
                if m:
                    start = i + m.start()
                    # Find the matching closing paren
                    depth_count = 0
                    j = start
                    while j < n:
                        if text[j] == '(':
                            depth_count += 1
                        elif text[j] == ')':
                            depth_count -= 1
                            if depth_count == 0:
                                # Found end of this item
                                item = text[start:j+1]
                                # Check if it's a drawing item
                                item_type_match = re.match(r'\((gr_text|gr_line|gr_rect|gr_poly|gr_arc|gr_circle|dimension)', item)
                                if item_type_match:
                                    # Check if it's NOT Edge.Cuts
                                    if '"Edge.Cuts"' not in item and 'Edge.Cuts' not in item:
                                        # Remove it
                                        removed += 1
                                        # Skip the item and any preceding whitespace/newline
                                        result.append(text[i:start])
                                        i = j + 1
                                        # Skip trailing newline
                                        if i < n and text[i] == '\n':
                                            i += 1
                                        break
                                result.append(text[i:j+1])
                                i = j + 1
                                break
                        j += 1
                    else:
                        result.append(text[i])
                        i += 1
                    continue
        
        result.append(text[i])
        i += 1
    
    print(f"Removed {removed} non-Edge.Cuts drawings")
    return ''.join(result)


# Better approach: use line-by-line S-expression parsing
def strip_drawings(content):
    """Remove top-level drawing elements that aren't on Edge.Cuts."""
    lines = content.split('\n')
    result_lines = []
    skip_depth = 0
    paren_depth = 0
    skip_start_depth = None
    removed = 0
    
    DRAWING_TYPES = ('gr_text', 'gr_line', 'gr_rect', 'gr_poly', 'gr_arc', 'gr_circle', 'dimension')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Check if this is a top-level drawing item (paren_depth == 1 means inside kicad_pcb)
        if paren_depth == 1 and skip_depth == 0:
            is_drawing = any(stripped.startswith(f'({t}') for t in DRAWING_TYPES)
            if is_drawing:
                # Collect this entire item to check if it's Edge.Cuts
                item_lines = [line]
                depth = line.count('(') - line.count(')')
                j = i + 1
                while depth > 0 and j < len(lines):
                    item_lines.append(lines[j])
                    depth += lines[j].count('(') - lines[j].count(')')
                    j += 1
                
                item_text = '\n'.join(item_lines)
                
                if 'Edge.Cuts' not in item_text:
                    # Skip this item
                    removed += 1
                    # Update paren depth
                    for il in item_lines:
                        paren_depth += il.count('(') - il.count(')')
                    i = j
                    continue
                else:
                    # Keep it - Edge.Cuts drawing
                    for il in item_lines:
                        paren_depth += il.count('(') - il.count(')')
                    result_lines.extend(item_lines)
                    i = j
                    continue
        
        paren_depth += line.count('(') - line.count(')')
        result_lines.append(line)
        i += 1
    
    print(f"Removed {removed} non-Edge.Cuts board drawings")
    return '\n'.join(result_lines)


new_content = strip_drawings(content)

with open(PCB_PATH, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done.")
