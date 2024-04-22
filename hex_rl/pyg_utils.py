def brighten(x, y):
    return x + y if x + y < 255 else 255


def brighten_color(x, offset):
    return tuple(brighten(x, offset) for x in x)