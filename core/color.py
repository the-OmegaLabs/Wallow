def rgb_to_hsv(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx - mn

    h = 0 if df == 0 else (
        60 * ((g - b) / df + 4) if mx == r else
        60 * ((b - r) / df + 2) if mx == g else
        60 * ((r - g) / df + 0)
    )
    s = 0 if mx == 0 else df / mx
    v = mx
    return (h % 360, s, v)


def cmyk_to_rgb(c, m, y, k):
    r = 255 * (1 - c) * (1 - k)
    g = 255 * (1 - m) * (1 - k)
    b = 255 * (1 - y) * (1 - k)
    return (int(r), int(g), int(b))