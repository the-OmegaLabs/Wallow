from core import WallowImage


def grayscale_filter(pixel_data):
    processed = bytearray()
    for i in range(0, len(pixel_data), 3):
        r, g, b = pixel_data[i:i+3]
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
        processed.extend([gray, gray, gray])
    return processed

def sepia_filter(pixel_data):
    processed = bytearray()
    for i in range(0, len(pixel_data), 3):
        r, g, b = pixel_data[i:i+3]
        new_r = min(255, int(r * 0.393 + g * 0.769 + b * 0.189))
        new_g = min(255, int(r * 0.349 + g * 0.686 + b * 0.168))
        new_b = min(255, int(r * 0.272 + g * 0.534 + b * 0.131))
        processed.extend([new_r, new_g, new_b])
    return processed


def apply_color_matrix(image, matrix):
    """应用颜色变换矩阵 (RGB空间)"""
    if image.mode != 'RGB':
        image = image.convert('RGB')

    r_m = matrix
    g_m = matrix
    b_m = matrix

    processed = bytearray()
    for i in range(0, len(image.data), 3):
        r, g, b = image.data[i:i + 3]
        nr = min(255, int(r * r_m + g * r_m + b * r_m))
        ng = min(255, int(r * g_m + g * g_m + b * g_m))
        nb = min(255, int(r * b_m + g * b_m + b * b_m))
        processed.extend([nr, ng, nb])

    return WallowImage(processed, image.mode, image.size)