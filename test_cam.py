import arcade
window = arcade.Window(1280, 640)
c = arcade.Camera2D(viewport=arcade.LBWH(0,0,1280,640), projection=arcade.LRBT(0,1280,0,640))
print("Pos:", c.position)
print("Bottom left:", c.bottom_left)
