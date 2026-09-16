import os
import re
import shutil

# 1. Create apple sprite (copy vial for now)
shutil.copyfile('assets/sprites/item_vial.png', 'assets/sprites/item_apple.png')
print("Created apple sprite.")

# 2. Update maps
maps = ['assets/maps/level_01.tmx', 'assets/maps/level_02.tmx', 'assets/maps/level_test.tmx']
for m in maps:
    with open(m, 'r') as f:
        content = f.read()

    # Find the key object and its coordinates to place an apple somewhere nearby
    # For simplicity, we just add an apple near the vial or spawn.
    # Let's just find the vial x,y and add an apple 64 pixels away
    vial_match = re.search(r'<object.*?name="vial".*?x="(\d+)".*?y="(\d+)".*?>', content)
    if vial_match:
        x, y = int(vial_match.group(1)), int(vial_match.group(2))
        apple_x, apple_y = x + 64, y
        # insert apple object
        apple_obj = f'\n  <object name="apple" class="apple" type="apple" x="{apple_x}" y="{apple_y}" width="32" height="32"/>\n'
        content = content.replace('</objectgroup>\n <objectgroup id="15" name="Items">', '</objectgroup>\n <objectgroup id="15" name="Items">' + apple_obj)
        print(f"Added apple to {m}")

    # Replace key with NPC
    # We need to find the <object ... class="key" ...> block
    key_pattern = r'(<object[^>]*name="key"[^>]*class="key"[^>]*type="key"[^>]*>[\s\S]*?</object>)'
    
    def repl_key(match):
        block = match.group(1)
        block = block.replace('name="key"', 'name="npc"').replace('class="key"', 'class="npc"').replace('type="key"', 'type="npc"')
        # add wants_item and lines to properties
        if '<properties>' in block:
            block = block.replace('</properties>', ' <property name="wants_item" type="string" value="apple"/>\n    <property name="lines" type="string" value="J\'ai tellement faim...|Donne-moi une pomme !"/>\n   </properties>')
        else:
            block = block.replace('/>', '>\n   <properties>\n    <property name="wants_item" type="string" value="apple"/>\n    <property name="lines" type="string" value="J\'ai tellement faim...|Donne-moi une pomme !"/>\n   </properties>\n  </object>')
            block = block.replace('</object>\n  </object>', '</object>') # fix in case it wasn't self closing
        return block

    new_content = re.sub(key_pattern, repl_key, content)
    with open(m, 'w') as f:
        f.write(new_content)
    print(f"Updated {m}")
