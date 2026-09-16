import re
import shutil

# 1. Create shield sprite (copy item_key.png or item_torch.png for now)
shutil.copyfile('assets/sprites/item_vial.png', 'assets/sprites/item_shield.png')
print("Created shield sprite.")

# 2. Update maps
maps = ['assets/maps/level_01.tmx', 'assets/maps/level_02.tmx', 'assets/maps/level_test.tmx']
for m in maps:
    with open(m, 'r') as f:
        content = f.read()

    # Replace all "apple" with "shield" (this will update the item object as well)
    content = content.replace('name="apple"', 'name="shield"')
    content = content.replace('class="apple"', 'class="shield"')
    content = content.replace('type="apple"', 'type="shield"')
    content = content.replace('value="apple"', 'value="shield"')

    # Update dialog lines
    content = content.replace(
        'value="J\'ai tellement faim...|Donne-moi une pomme !"',
        'value="J\'ai besoin d\'une défense...|Donne-moi un bouclier !"'
    )

    with open(m, 'w') as f:
        f.write(content)
    print(f"Updated {m}")
