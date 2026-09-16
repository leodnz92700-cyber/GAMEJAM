from src.mechanics.map_loader import load_map
m = load_map('map.tmx')
print('  ' + ''.join(str(i%10) for i in range(10)))
for row in range(35, 28, -1):
    line = ''
    for col in range(10):
        if not m.walkable[row][col]:
            line += '#'
        else:
            line += '.'
    print(f'{row:2d}{line}')
