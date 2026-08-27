import json
with open('build/icio500/drc_final3.json', encoding='utf-8') as f:
    report = json.load(f)
print('Violations:', len(report['violations']))
for v in report['violations']:
    t = v.get('type', '')
    if t not in ('padstack', 'silk_overlap', 'silk_over_copper', 'lib_footprint_issues', 'lib_footprint_mismatch'):
        print(f'[{t}]')
