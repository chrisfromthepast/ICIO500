"""
Investigate the isolated_copper on GND F.Cu zone.
The DRC says: Zone [gnd] on F.Cu, priority 0 @ (51.12, 55.48)

This is the zone origin point. The isolated island is somewhere in the board
where a patch of GND copper fill on F.Cu is not connected to any via or pad.

Strategy: find all F.Cu GND zone fills and look for the island.
Also look for any copper around the board origin at (51.12, 55.48).
"""
import json, re

# Read the DRC report for more detail
with open('build/icio500/drc_clean2.json', encoding='utf-8') as f:
    report = json.load(f)

for v in report['violations']:
    if v.get('type') == 'isolated_copper':
        print('ISOLATED COPPER violation details:')
        print('  Description:', v.get('description', ''))
        print('  Items:')
        for item in v.get('items', []):
            pos = item.get('pos', {})
            print(f'    {item.get("description","")}')
            print(f'    position: ({pos.get("x",0)}, {pos.get("y",0)})')
            print(f'    layer: {item.get("layer","")}')
            print(f'    net: {item.get("net","")}')
            # Any extra fields
            for k, val in item.items():
                if k not in ('description', 'pos', 'layer', 'net', 'type'):
                    print(f'    {k}: {val}')

# Also examine the PCB around (51.12, 55.48) - that's the zone's bounding box origin
# Look for zones and their fill areas
content = open('build/icio500/icio500.kicad_pcb', encoding='utf-8').read()

# Find GND zones on F.Cu
zone_count = 0
for m in re.finditer(r'\t\(zone\b', content):
    start = m.start()
    # Grab first 500 chars to check layer and net
    snippet = content[start:start+300]
    if 'F.Cu' in snippet and '"gnd"' in snippet:
        zone_count += 1
        # Get net name and layer
        net_m = re.search(r'\(net "([^"]+)"\)', snippet)
        layer_m = re.search(r'\(layer "([^"]+)"\)', snippet)
        # Get zone position/name
        name_m = re.search(r'\(name "([^"]*)"\)', snippet)
        uuid_m = re.search(r'\(uuid "([^"]+)"\)', snippet)
        print(f'\nGND F.Cu zone {zone_count}:')
        if layer_m: print(f'  layer: {layer_m.group(1)}')
        if net_m: print(f'  net: {net_m.group(1)}')
        if name_m: print(f'  name: {name_m.group(1)}')
        if uuid_m: print(f'  uuid: {uuid_m.group(1)[:8]}...')
        # Check for fill islands
        if 'filled_polygon' in content[start:start+5000]:
            print('  Has filled_polygon data')
        # Check for no_connect or connect_pads settings
        if 'connect_pads' in snippet:
            cp_m = re.search(r'\(connect_pads\s+(\w+)', snippet)
            if cp_m: print(f'  connect_pads mode: {cp_m.group(1)}')
        if 'island_removal_mode' in content[start:start+600]:
            irm = re.search(r'\(island_removal_mode (\d+)\)', content[start:start+600])
            if irm: print(f'  island_removal_mode: {irm.group(1)}')

print(f'\nTotal GND F.Cu zones: {zone_count}')
