with open('tools/legacy_scripts/autoroute_main.py', 'r', encoding='utf-8') as f:
    text = f.read()
text = text.replace("self.grid = {'F.Cu': {}, 'B.Cu': {}}", "self.grid = {'F.Cu': {}, 'In1.Cu': {}, 'In2.Cu': {}, 'B.Cu': {}}")
with open('tools/legacy_scripts/autoroute_main.py', 'w', encoding='utf-8') as f:
    f.write(text)
