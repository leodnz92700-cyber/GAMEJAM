from src.mechanics.map_loader import load_map
m = load_map('map.tmx')
col = 160 // 32
arcade_y = 1280 - 257
row = int(arcade_y // 32)
print(f'col={col}, row={row}')
print('above:', not m.walkable[row+1][col])
print('below:', not m.walkable[row-1][col])
print('left:', not m.walkable[row][col-1])
print('right:', not m.walkable[row][col+1])
