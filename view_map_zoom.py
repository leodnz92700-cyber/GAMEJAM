from src.mechanics.map_loader import load_map
m = load_map('map.tmx')
print('  4567')
for r in range(35, 29, -1):
    s = ''
    for c in range(4, 8):
        s += '#' if not m.walkable[r][c] else '.'
    print(f'{r:2d}{s}')
