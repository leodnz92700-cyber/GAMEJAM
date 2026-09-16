from src.mechanics.map_loader import load_map
m = load_map('map.tmx')
lines = []
for row in range(39, -1, -1):
    line = ''
    for col in range(80):
        if not m.walkable[row][col]:
            line += '#'
        else:
            line += '.'
    lines.append(f'{row:2d} {line}')
with open('map_full.txt', 'w') as f:
    f.write('\n'.join(lines))
