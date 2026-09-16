def get_shifted(x, y, w, h, rot):
    # x,y are Tiled top-left.
    if rot == 90:
        return x - h, y
    elif rot == 180:
        return x - w, y - h
    elif rot == -90 or rot == 270:
        return x, y - w
    return x, y

print(get_shifted(160, 257, 32, 32, 90))
