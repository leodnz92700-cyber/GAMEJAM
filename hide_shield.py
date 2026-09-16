import re

def hide_shield(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    torches = re.findall(r'<object[^>]*?name="torch"[^>]*?x="(\d+)"[^>]*?y="(\d+)"', content)
    if not torches:
        print(f"No torches found in {filepath}")
        return

    # Pick the 3rd to last torch, to make it somewhat deep into the level
    target_torch = torches[max(0, len(torches) - 3)]
    torch_x = int(target_torch[0])
    torch_y = int(target_torch[1])

    def repl_shield(match):
        return f'<object id="999" name="shield" class="shield" type="shield" x="{torch_x}" y="{torch_y + 32}" width="32" height="32"/>'
        
    content = re.sub(r'<object id="999" name="shield" class="shield" type="shield"[^>]*/>', repl_shield, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Hid shield in {filepath} at {torch_x}, {torch_y + 32}')

maps = ['assets/maps/level_01.tmx', 'assets/maps/level_02.tmx', 'assets/maps/level_test.tmx']
for m in maps:
    hide_shield(m)
