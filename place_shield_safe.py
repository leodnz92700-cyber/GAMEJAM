import re

def place_shield_safely(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the vial to get a guaranteed safe walkable coordinate
    vial_match = re.search(r'<object[^>]*?name="vial"[^>]*?x="(\d+)"[^>]*?y="(\d+)"', content)
    if vial_match:
        safe_x = int(vial_match.group(1)) + 32
        safe_y = int(vial_match.group(2))
    else:
        # Fallback to the first torch's exact coordinates, which should be walkable floor
        torches = re.findall(r'<object[^>]*?name="torch"[^>]*?x="(\d+)"[^>]*?y="(\d+)"', content)
        safe_x = int(torches[0][0])
        safe_y = int(torches[0][1])

    def repl_shield(match):
        return f'<object id="999" name="shield" class="shield" type="shield" x="{safe_x}" y="{safe_y}" width="32" height="32"/>'
        
    content = re.sub(r'<object id="999" name="shield" class="shield" type="shield"[^>]*/>', repl_shield, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Placed shield safely in {filepath} at {safe_x}, {safe_y}')

maps = ['assets/maps/level_01.tmx', 'assets/maps/level_02.tmx', 'assets/maps/level_test.tmx']
for m in maps:
    place_shield_safely(m)
