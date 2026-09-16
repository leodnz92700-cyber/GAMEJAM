from src.mechanics.map_loader import load_map
m = load_map('map.tmx')
print('  ' + ''.join(str(i%10) for i in range(16)))
for row in range(39, 24, -1):
    line = ''
    for col in range(16):
        if not m.walkable[row][col]:
            line += '#'
        elif row == 34 and col == 7:
            line += 'M'
        elif row == 31 and col == 5:
            line += '2'
        else:
            line += '.'
    print(f'{row:2d}{line}')
