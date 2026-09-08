import sys
with open('tools/legacy_scripts/autoroute_sat.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('GRID_RESOLUTION = 0.05', 'GRID_RESOLUTION = 0.2')
text = text.replace('len(open_set) > 100000', 'len(open_set) > 200000')

with open('tools/legacy_scripts/autoroute_sat.py', 'w', encoding='utf-8') as f:
    f.write(text)
