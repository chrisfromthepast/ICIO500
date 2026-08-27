"""
ICIO 500 PCB Autorouter
Parses KiCad PCB S-expressions, identifies disconnected pads,
and generates trace segments to complete the routing.
"""
import re
import math
import uuid

PCB_PATH = 'build/icio500/icio500.kicad_pcb'

def parse_pcb():
    with open(PCB_PATH, encoding='utf-8') as f:
        lines = f.readlines()
    pcb_text = ''.join(lines)
    
    # === PARSE FOOTPRINTS AND PADS ===
    # Strategy: walk through lines, track footprint context
    pads = []  # list of {net, abs_x, abs_y, ref, pad_num, layer}
    
    # Split into footprint blocks
    fp_starts = []
    for i, line in enumerate(lines):
        if line.strip().startswith('(footprint '):
            fp_starts.append(i)
    
    for fi, fp_line_start in enumerate(fp_starts):
        fp_line_end = fp_starts[fi + 1] if fi + 1 < len(fp_starts) else len(lines)
        fp_lines = lines[fp_line_start:fp_line_end]
        fp_text = ''.join(fp_lines)
        
        # Get footprint position
        at_match = re.search(r'\(at ([\d.e-]+) ([\d.e-]+)(?: ([\d.e-]+))?\)', fp_text[:500])
        if not at_match:
            continue
        fp_x = float(at_match.group(1))
        fp_y = float(at_match.group(2))
        fp_rot = float(at_match.group(3)) if at_match.group(3) else 0.0
        
        # Get reference
        ref_match = re.search(r'"Reference" "([^"]+)"', fp_text[:1500])
        ref = ref_match.group(1) if ref_match else '??'
        
        # Get footprint layer
        layer_match = re.search(r'\n\t\t\(layer "([^"]+)"\)', fp_text[:300])
        fp_layer = layer_match.group(1) if layer_match else 'F.Cu'
        
        # KiCad rotation: positive = CCW in schematic coords
        # For PCB, need to negate for standard math rotation
        rot_rad = math.radians(-fp_rot)
        cos_r = math.cos(rot_rad)
        sin_r = math.sin(rot_rad)
        
        # Find all pad blocks
        # Each pad starts with (pad "N" and we look for (at and (net within the pad block
        pad_matches = list(re.finditer(r'\(pad "(\d+)" ', fp_text))
        
        for pi, pm in enumerate(pad_matches):
            pad_num = pm.group(1)
            # Extract text from this pad to the next pad (or end of footprint)
            start = pm.start()
            end = pad_matches[pi + 1].start() if pi + 1 < len(pad_matches) else len(fp_text)
            pad_block = fp_text[start:end]
            
            # Get pad local position
            at_match2 = re.search(r'\(at ([\d.e-]+) ([\d.e-]+)', pad_block)
            if not at_match2:
                continue
            px = float(at_match2.group(1))
            py = float(at_match2.group(2))
            
            # Get pad net
            net_match = re.search(r'\(net "([^"]+)"\)', pad_block)
            if not net_match:
                continue
            net = net_match.group(1)
            
            # Compute absolute position
            abs_x = fp_x + px * cos_r - py * sin_r
            abs_y = fp_y + px * sin_r + py * cos_r
            
            pads.append({
                'net': net,
                'abs_x': round(abs_x, 4),
                'abs_y': round(abs_y, 4),
                'ref': ref,
                'pad_num': pad_num,
                'layer': fp_layer,
            })
    
    # === PARSE EXISTING SEGMENTS ===
    segments = []  # list of {sx, sy, ex, ey, net, layer, width}
    for m in re.finditer(
        r'\(segment\s+\(start ([\d.e-]+) ([\d.e-]+)\)\s+\(end ([\d.e-]+) ([\d.e-]+)\)\s+\(width ([\d.e-]+)\)\s+\(layer "([^"]+)"\)\s+\(net "([^"]+)"\)',
        pcb_text
    ):
        segments.append({
            'sx': float(m.group(1)), 'sy': float(m.group(2)),
            'ex': float(m.group(3)), 'ey': float(m.group(4)),
            'width': float(m.group(5)),
            'layer': m.group(6),
            'net': m.group(7),
        })
    
    # === PARSE VIAS ===
    vias = []
    for m in re.finditer(
        r'\(via\s+\(at ([\d.e-]+) ([\d.e-]+)\).*?\(net "([^"]+)"\)',
        pcb_text, re.DOTALL
    ):
        vias.append({
            'x': float(m.group(1)), 'y': float(m.group(2)),
            'net': m.group(3),
        })
    
    return pads, segments, vias, lines, pcb_text


def build_connectivity(pads, segments, vias, tolerance=0.5):
    """Build a graph of connected points for each net."""
    from collections import defaultdict
    
    net_points = defaultdict(set)  # net -> set of (x,y) connected points
    
    # Add segment endpoints
    for seg in segments:
        net = seg['net']
        net_points[net].add((round(seg['sx'], 2), round(seg['sy'], 2)))
        net_points[net].add((round(seg['ex'], 2), round(seg['ey'], 2)))
    
    # Add via positions
    for via in vias:
        net_points[via['net']].add((round(via['x'], 2), round(via['y'], 2)))
    
    # Check which pads are connected (have a segment endpoint near them)
    disconnected = []  # pads that have no segment endpoint nearby
    connected = []
    
    for pad in pads:
        net = pad['net']
        points = net_points.get(net, set())
        px, py = pad['abs_x'], pad['abs_y']
        
        found = False
        for ex, ey in points:
            if abs(px - ex) < tolerance and abs(py - ey) < tolerance:
                found = True
                break
        
        if found:
            connected.append(pad)
        else:
            disconnected.append(pad)
    
    return disconnected, connected, net_points


def find_nearest_connected_point(pad, net_points, tolerance=0.5):
    """Find the nearest existing segment endpoint on the same net."""
    net = pad['net']
    points = net_points.get(net, set())
    if not points:
        return None
    
    px, py = pad['abs_x'], pad['abs_y']
    best = None
    best_dist = float('inf')
    
    for ex, ey in points:
        dist = math.sqrt((px - ex)**2 + (py - ey)**2)
        if dist < best_dist and dist > tolerance:  # Don't connect to self
            best_dist = dist
            best = (ex, ey)
    
    return best


def find_nearest_pad_on_net(pad, all_pads, tolerance=0.5):
    """Find the nearest other pad on the same net."""
    net = pad['net']
    px, py = pad['abs_x'], pad['abs_y']
    best = None
    best_dist = float('inf')
    
    for other in all_pads:
        if other['net'] != net:
            continue
        ox, oy = other['abs_x'], other['abs_y']
        dist = math.sqrt((px - ox)**2 + (py - oy)**2)
        if dist < best_dist and dist > tolerance:
            best_dist = dist
            best = other
    
    return best


def generate_l_route(start_x, start_y, end_x, end_y, net, width=0.25, layer="F.Cu"):
    """Generate an L-shaped route (horizontal then vertical) between two points."""
    segs = []
    mid_x = end_x
    mid_y = start_y
    
    # Horizontal segment
    if abs(start_x - mid_x) > 0.01:
        segs.append({
            'sx': start_x, 'sy': start_y,
            'ex': mid_x, 'ey': mid_y,
            'net': net, 'width': width, 'layer': layer,
        })
    
    # Vertical segment
    if abs(mid_y - end_y) > 0.01:
        segs.append({
            'sx': mid_x, 'sy': mid_y,
            'ex': end_x, 'ey': end_y,
            'net': net, 'width': width, 'layer': layer,
        })
    
    return segs


def segment_to_kicad(seg):
    """Convert a segment dict to KiCad S-expression."""
    uid = str(uuid.uuid4())
    return (
        f'\t(segment\n'
        f'\t\t(start {seg["sx"]:.4f} {seg["sy"]:.4f})\n'
        f'\t\t(end {seg["ex"]:.4f} {seg["ey"]:.4f})\n'
        f'\t\t(width {seg["width"]})\n'
        f'\t\t(layer "{seg["layer"]}")\n'
        f'\t\t(net "{seg["net"]}")\n'
        f'\t\t(uuid "{uid}")\n'
        f'\t)\n'
    )


def main():
    print("Parsing PCB...")
    pads, segments, vias, lines, pcb_text = parse_pcb()
    print(f"  Found {len(pads)} pads with nets, {len(segments)} segments, {len(vias)} vias")
    
    print("\nAnalyzing connectivity...")
    disconnected, connected, net_points = build_connectivity(pads, segments, vias)
    
    print(f"\n  CONNECTED pads: {len(connected)}")
    print(f"  DISCONNECTED pads: {len(disconnected)}")
    
    # Skip single-pad nets (nothing to connect to)
    # Group disconnected pads by net
    from collections import defaultdict
    disc_by_net = defaultdict(list)
    for pad in disconnected:
        disc_by_net[pad['net']].append(pad)
    
    # Skip nets that are only single pads with no existing traces
    skip_nets = {'audio_out_r', 'p18', 'p19', 'p20'}  # Unused/unconnected by design
    
    new_segments = []
    
    print("\n=== ROUTING PLAN ===")
    for net, disc_pads in sorted(disc_by_net.items()):
        if net in skip_nets:
            print(f"\n  [{net}] SKIPPED (unused/single-pad)")
            continue
        
        print(f"\n  [{net}] {len(disc_pads)} disconnected pad(s)")
        
        for pad in disc_pads:
            print(f"    Pad: {pad['ref']} pin {pad['pad_num']} at ({pad['abs_x']:.2f}, {pad['abs_y']:.2f})")
            
            # Try to find nearest existing trace endpoint
            target = find_nearest_connected_point(pad, net_points)
            
            if target:
                tx, ty = target
                print(f"    -> Route to existing trace at ({tx:.2f}, {ty:.2f})")
                
                # Determine trace width based on net type
                if net in ('gnd', 'v_plus', 'v_minus', 'daisy_5v_power'):
                    width = 0.4  # Power nets get wider traces
                else:
                    width = 0.25  # Signal nets
                
                route_segs = generate_l_route(
                    pad['abs_x'], pad['abs_y'],
                    tx, ty,
                    net, width=width, layer="F.Cu"
                )
                new_segments.extend(route_segs)
                
                # Add the new endpoints to net_points so subsequent pads can find them
                for seg in route_segs:
                    net_points[net].add((round(seg['sx'], 2), round(seg['sy'], 2)))
                    net_points[net].add((round(seg['ex'], 2), round(seg['ey'], 2)))
            else:
                # Try to find another pad on the same net
                other = find_nearest_pad_on_net(pad, pads + connected)
                if other:
                    print(f"    -> Route to pad {other['ref']} pin {other['pad_num']} at ({other['abs_x']:.2f}, {other['abs_y']:.2f})")
                    width = 0.4 if net in ('gnd', 'v_plus', 'v_minus', 'daisy_5v_power') else 0.25
                    route_segs = generate_l_route(
                        pad['abs_x'], pad['abs_y'],
                        other['abs_x'], other['abs_y'],
                        net, width=width, layer="F.Cu"
                    )
                    new_segments.extend(route_segs)
                    for seg in route_segs:
                        net_points[net].add((round(seg['sx'], 2), round(seg['sy'], 2)))
                        net_points[net].add((round(seg['ex'], 2), round(seg['ey'], 2)))
                else:
                    print(f"    -> WARNING: No target found on net {net}!")
    
    if not new_segments:
        print("\nNo new segments to add!")
        return
    
    print(f"\n=== WRITING {len(new_segments)} NEW SEGMENTS ===")
    
    # Generate KiCad segment text
    new_seg_text = '\n'.join(segment_to_kicad(seg) for seg in new_segments)
    
    # Insert before the closing ) of the PCB file
    # Find the last line with just ")"
    insert_pos = pcb_text.rfind('\n)')
    if insert_pos == -1:
        print("ERROR: Could not find insertion point!")
        return
    
    new_pcb = pcb_text[:insert_pos] + '\n' + new_seg_text + pcb_text[insert_pos:]
    
    with open(PCB_PATH, 'w', encoding='utf-8') as f:
        f.write(new_pcb)
    
    print(f"Successfully wrote {len(new_segments)} new trace segments to {PCB_PATH}")
    
    # Verify
    print("\n=== VERIFICATION ===")
    pads2, segments2, vias2, _, _ = parse_pcb()
    disc2, conn2, _ = build_connectivity(pads2, segments2, vias2)
    remaining = [p for p in disc2 if p['net'] not in skip_nets]
    print(f"  Previously disconnected: {len(disconnected)}")
    print(f"  Now disconnected: {len(disc2)} ({len(remaining)} excluding skipped nets)")
    if remaining:
        for p in remaining:
            print(f"    Still disconnected: {p['ref']} pad {p['pad_num']} net={p['net']}")


if __name__ == '__main__':
    main()
