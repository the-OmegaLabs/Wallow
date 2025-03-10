"""
颜色空间转换工具
"""

import math


def rgb_to_hsv(r, g, b):
    """
    将RGB颜色值转换为HSV

    参数:
        r, g, b: 0-255范围内的RGB值

    返回:
        h: 0-360度的色相
        s: 0-100%的饱和度
        v: 0-100%的明度
    """
    r /= 255
    g /= 255
    b /= 255

    max_val = max(r, g, b)
    min_val = min(r, g, b)
    diff = max_val - min_val

    v = max_val * 100

    if max_val == 0:
        s = 0
    else:
        s = (diff / max_val) * 100

    if diff == 0:
        h = 0
    elif max_val == r:
        h = 60 * ((g - b) / diff % 6)
    elif max_val == g:
        h = 60 * ((b - r) / diff + 2)
    else:  # max_val == b
        h = 60 * ((r - g) / diff + 4)

    if h < 0:
        h += 360

    return h, s, v


def hsv_to_rgb(h, s, v):
    """
    将HSV颜色值转换为RGB

    参数:
        h: 0-360度的色相
        s: 0-100%的饱和度
        v: 0-100%的明度

    返回:
        r, g, b: 0-255范围内的RGB值
    """
    s /= 100
    v /= 100

    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:  # 300 <= h < 360
        r, g, b = c, 0, x

    r = round((r + m) * 255)
    g = round((g + m) * 255)
    b = round((b + m) * 255)

    return r, g, b


def rgb_to_lab(r, g, b):
    """
    将RGB颜色值转换为CIE Lab

    参数:
        r, g, b: 0-255范围内的RGB值

    返回:
        L: 0-100的亮度值
        a: 绿-红色轴
        b: 蓝-黄色轴
    """
    # RGB转XYZ
    r /= 255
    g /= 255
    b /= 255

    # sRGB到线性RGB的转换
    r = _gamma_to_linear(r)
    g = _gamma_to_linear(g)
    b = _gamma_to_linear(b)

    # 线性RGB到XYZ的转换矩阵
    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041

    # XYZ到Lab的转换
    # 参考白点 (D65)
    x_ref = 0.95047
    y_ref = 1.0
    z_ref = 1.08883

    x /= x_ref
    y /= y_ref
    z /= z_ref

    x = _xyz_to_lab(x)
    y = _xyz_to_lab(y)
    z = _xyz_to_lab(z)

    L = max(0, 116 * y - 16)
    a = 500 * (x - y)
    b = 200 * (y - z)

    return L, a, b


def lab_to_rgb(L, a, b):
    """
    将CIE Lab颜色值转换为RGB

    参数:
        L: 0-100的亮度值
        a: 绿-红色轴
        b: 蓝-黄色轴

    返回:
        r, g, b: 0-255范围内的RGB值
    """
    # 参考白点 (D65)
    x_ref = 0.95047
    y_ref = 1.0
    z_ref = 1.08883

    # Lab到XYZ的转换
    y = (L + 16) / 116
    x = a / 500 + y
    z = y - b / 200

    x = _lab_to_xyz(x) * x_ref
    y = _lab_to_xyz(y) * y_ref
    z = _lab_to_xyz(z) * z_ref

    # XYZ到线性RGB的转换矩阵
    r = x * 3.2404542 + y * -1.5371385 + z * -0.4985314
    g = x * -0.9692660 + y * 1.8760108 + z * 0.0415560
    b = x * 0.0556434 + y * -0.2040259 + z * 1.0572252

    # 线性RGB到sRGB的转换
    r = _linear_to_gamma(r)
    g = _linear_to_gamma(g)
    b = _linear_to_gamma(b)

    r = round(r * 255)
    g = round(g * 255)
    b = round(b * 255)

    return (
        max(0, min(255, r)),
        max(0, min(255, g)),
        max(0, min(255, b))
    )


def _gamma_to_linear(c):
    """sRGB gamma到线性空间的转换"""
    if c <= 0.04045:
        return c / 12.92
    else:
        return ((c + 0.055) / 1.055) ** 2.4


def _linear_to_gamma(c):
    """线性空间到sRGB gamma的转换"""
    if c <= 0.0031308:
        return c * 12.92
    else:
        return 1.055 * (c ** (1 / 2.4)) - 0.055


def _xyz_to_lab(t):
    """XYZ到Lab的辅助函数"""
    if t > 0.008856:
        return t ** (1 / 3)
    else:
        return (t * 903.3 + 16) / 116


def _lab_to_xyz(t):
    """Lab到XYZ的辅助函数"""
    if t > 0.206893:
        return t ** 3
    else:
        return (t * 116 - 16) / 903.3
