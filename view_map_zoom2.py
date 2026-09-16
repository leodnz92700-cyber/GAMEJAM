from src.mechanics.map_loader import load_map
m = load_map('map.tmx')
print('walkable[31][5]:', m.walkable[31][5])
print('walkable[31][4]:', m.walkable[31][4])
print('walkable[31][6]:', m.walkable[31][6])
