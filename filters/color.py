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
    # Matrix should be 3x3
    r_matrix, g_matrix, b_matrix = matrix  # Unpack three rows

    processed = bytearray()
    for i in range(0, len(image._pixel_data), 3):
        r, g, b = image._pixel_data[i:i + 3]
        nr = min(255, int(r * r_matrix[0] + g * r_matrix[1] + b * r_matrix[2]))
        ng = min(255, int(r * g_matrix[0] + g * g_matrix[1] + b * g_matrix[2]))
        nb = min(255, int(r * b_matrix[0] + g * b_matrix[1] + b * b_matrix[2]))
        processed.extend([nr, ng, nb])

    return WallowImage(processed, image.color_mode, (image.width, image.height))