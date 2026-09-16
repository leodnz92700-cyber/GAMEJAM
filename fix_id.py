import re

maps = ['assets/maps/level_01.tmx', 'assets/maps/level_02.tmx', 'assets/maps/level_test.tmx']
for m in maps:
    with open(m, 'r') as f:
        content = f.read()
    
    # Give it an ID like 999 to avoid collisions
    content = content.replace('<object name="apple" class="apple" type="apple"', '<object id="999" name="apple" class="apple" type="apple"')
    
    with open(m, 'w') as f:
        f.write(content)
    print(f'Fixed {m}')
