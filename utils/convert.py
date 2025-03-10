"""
格式转换工具
"""

import os

from ..core import WallowImage


def convert_format(input_path, output_path=None, format=None):
    """
    转换图像格式

    参数:
        input_path: 输入图像路径
        output_path: 输出图像路径 (可选)
        format: 目标格式 (如 'png', 'bmp', 'jpg')

    返回:
        输出文件路径
    """
    img = WallowImage.open(input_path)

    if output_path is None:
        # 如果没有指定输出路径，使用相同目录和文件名但扩展名不同
        if format is None:
            raise ValueError("必须指定输出路径或目标格式")

        dir_name = os.path.dirname(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(dir_name, f"{base_name}.{format}")
    elif format is not None:
        # 如果指定了格式，确保输出路径使用正确的扩展名
        dir_name = os.path.dirname(output_path)
        base_name = os.path.splitext(os.path.basename(output_path))[0]
        output_path = os.path.join(dir_name, f"{base_name}.{format}")

    img.save(output_path)
    return output_path


def convert_color_mode(image, target_mode):
    """
    转换图像的颜色模式

    参数:
        image: WallowImage实例或图像文件路径
        target_mode: 目标颜色模式 ('RGB', 'RGBA', 'L')

    返回:
        转换后的WallowImage实例
    """
    if isinstance(image, str):
        img = WallowImage.open(image)
    else:
        img = image

    # 如果已经是目标模式，直接返回
    if img.color_mode == target_mode:
        return img

    # RGB转RGBA
    if img.color_mode == 'RGB' and target_mode == 'RGBA':
        return _rgb_to_rgba(img)

    # RGBA转RGB
    elif img.color_mode == 'RGBA' and target_mode == 'RGB':
        return _rgba_to_rgb(img)

    # RGB或RGBA转灰度
    elif (img.color_mode in ['RGB', 'RGBA']) and target_mode == 'L':
        return _to_grayscale(img)

    # 灰度转RGB
    elif img.color_mode == 'L' and target_mode == 'RGB':
        return _grayscale_to_rgb(img)

    # 灰度转RGBA
    elif img.color_mode == 'L' and target_mode == 'RGBA':
        return _grayscale_to_rgba(img)

    else:
        raise ValueError(f"不支持从 {img.color_mode} 转换到 {target_mode}")


def _rgb_to_rgba(img):
    """RGB图像转换为RGBA"""
    width, height = img.dimensions
    new_pixel_data = bytearray(width * height * 4)

    for i in range(width * height):
        # 复制RGB值并添加不透明Alpha通道(255)
        r_idx = i * 3
        a_idx = i * 4
        new_pixel_data[a_idx] = img._pixel_data[r_idx]  # R
        new_pixel_data[a_idx + 1] = img._pixel_data[r_idx + 1]  # G
        new_pixel_data[a_idx + 2] = img._pixel_data[r_idx + 2]  # B
        new_pixel_data[a_idx + 3] = 255  # A

    return WallowImage(new_pixel_data, 'RGBA', (width, height))


def _rgba_to_rgb(img):
    """RGBA图像转换为RGB"""
    width, height = img.dimensions
    new_pixel_data = bytearray(width * height * 3)

    for i in range(width * height):
        # 只复制RGB值，丢弃Alpha通道
        a_idx = i * 4
        r_idx = i * 3
        new_pixel_data[r_idx] = img._pixel_data[a_idx]  # R
        new_pixel_data[r_idx + 1] = img._pixel_data[a_idx + 1]  # G
        new_pixel_data[r_idx + 2] = img._pixel_data[a_idx + 2]  # B

    return WallowImage(new_pixel_data, 'RGB', (width, height))


def _to_grayscale(img):
    """将RGB或RGBA图像转换为灰度图像"""
    width, height = img.dimensions
    new_pixel_data = bytearray(width * height)

    if img.color_mode == 'RGB':
        bytes_per_pixel = 3
    else:  # 'RGBA'
        bytes_per_pixel = 4

    for i in range(width * height):
        src_idx = i * bytes_per_pixel
        r = img._pixel_data[src_idx]
        g = img._pixel_data[src_idx + 1]
        b = img._pixel_data[src_idx + 2]

        # 使用亮度公式将RGB转换为灰度
        # L = 0.299 * R + 0.587 * G + 0.114 * B
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
        new_pixel_data[i] = gray

    return WallowImage(new_pixel_data, 'L', (width, height))


def _grayscale_to_rgb(img):
    """将灰度图像转换为RGB图像"""
    width, height = img.dimensions
    new_pixel_data = bytearray(width * height * 3)

    for i in range(width * height):
        # 将灰度值复制到R、G、B三个通道
        gray = img._pixel_data[i]
        dst_idx = i * 3
        new_pixel_data[dst_idx] = gray  # R
        new_pixel_data[dst_idx + 1] = gray  # G
        new_pixel_data[dst_idx + 2] = gray  # B

    return WallowImage(new_pixel_data, 'RGB', (width, height))


def _grayscale_to_rgba(img):
    """将灰度图像转换为RGBA图像"""
    width, height = img.dimensions
    new_pixel_data = bytearray(width * height * 4)

    for i in range(width * height):
        # 将灰度值复制到R、G、B三个通道，并添加不透明Alpha通道
        gray = img._pixel_data[i]
        dst_idx = i * 4
        new_pixel_data[dst_idx] = gray  # R
        new_pixel_data[dst_idx + 1] = gray  # G
        new_pixel_data[dst_idx + 2] = gray  # B
        new_pixel_data[dst_idx + 3] = 255  # A (不透明)

    return WallowImage(new_pixel_data, 'RGBA', (width, height))
