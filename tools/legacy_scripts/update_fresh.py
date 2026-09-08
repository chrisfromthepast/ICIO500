with open('tools/legacy_scripts/make_fresh_assembly.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace Satellite offsets
text = text.replace('(xyz 0.8 166.675 -119.05)', '(xyz -5.2 166.675 -119.05)')

# Replace Faceplate offsets
text = text.replace('(xyz -0.8 66.675 -19.05)', '(xyz 0.8 58.35 0)')

with open('tools/legacy_scripts/make_fresh_assembly.py', 'w', encoding='utf-8') as f:
    f.write(text)
