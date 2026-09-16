import re

def place_shield_at_wall(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all torches
    torches = re.findall(r'<object[^>]*?name="torch"[^>]*?x="(\d+)"[^>]*?y="(\d+)"', content)
    if not torches:
        print(f"No torches found in {filepath}")
        return

    # Pick the first torch (usually near the start/spawn, but on a wall)
    target_torch = torches[0]
    torch_x = int(target_torch[0])
    # Place it just below the torch, so it's on the floor against the wall
    torch_y = int(target_torch[1]) - 32

    def repl_shield(match):
        return f'<object id="999" name="shield" class="shield" type="shield" x="{torch_x}" y="{torch_y}" width="32" height="32"/>'
        
    content = re.sub(r'<object id="999" name="shield" class="shield" type="shield"[^>]*/>', repl_shield, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Placed shield against wall in {filepath} at {torch_x}, {torch_y}')

maps = ['assets/maps/level_01.tmx', 'assets/maps/level_02.tmx', 'assets/maps/level_test.tmx']
for m in maps:
    place_shield_at_wall(m)
