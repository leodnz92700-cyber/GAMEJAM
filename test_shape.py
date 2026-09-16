import arcade
tile_map = arcade.load_tilemap('map/tiled/map.tmx')
for obj in tile_map.object_lists['Entities']:
    if obj.name == 'Door2':
        print('Door2 shape:', obj.shape)
