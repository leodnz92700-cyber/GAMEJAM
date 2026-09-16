maps = ['assets/maps/level_01.tmx', 'assets/maps/level_02.tmx', 'assets/maps/level_test.tmx']
for m in maps:
    try:
        with open(m, 'r', encoding='cp1252') as f:
            content = f.read()
        with open(m, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed encoding for {m}')
    except Exception as e:
        print(f'Error on {m}: {e}')
