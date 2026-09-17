import arcade
from src import constants as C

def apply_letterbox(camera: arcade.Camera2D, width: int, height: int) -> None:
    if width == 0 or height == 0:
        return
    target_width, target_height = C.VIEWPORT_WIDTH, C.VIEWPORT_HEIGHT
    target_ratio = target_width / target_height
    window_ratio = width / height

    if window_ratio > target_ratio:
        new_height = height
        new_width = int(new_height * target_ratio)
        x_margin = (width - new_width) // 2
        y_margin = 0
    else:
        new_width = width
        new_height = int(new_width / target_ratio)
        y_margin = (height - new_height) // 2
        x_margin = 0
        
    camera.viewport = arcade.LBWH(x_margin, y_margin, new_width, new_height)
