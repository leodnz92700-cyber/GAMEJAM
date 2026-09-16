import re

def update_dialog(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace the old dialog
    old_dialog = r"J'ai besoin d'une défense\.\.\.\|Donne-moi un bouclier !"
    new_dialog = "Rends-moi mon bouclier...|J'en ai absolument besoin !"
    
    content = re.sub(old_dialog, new_dialog, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Updated dialog in {filepath}')

maps = ['assets/maps/level_01.tmx', 'assets/maps/level_02.tmx', 'assets/maps/level_test.tmx']
for m in maps:
    update_dialog(m)
