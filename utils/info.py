"""
图像信息工具
"""

import os
from ..core import WallowImage


def get_image_info(image_path_or_instance):
    """
    获取图像的详细信息

    参数:
        image_path_or_instance: 文件路径或WallowImage实例

    返回:
        包含图像信息的字典
    """
    if isinstance(image_path_or_instance, str):
        img = WallowImage.open(image_path_or_instance)
        file_path = image_path_or_instance
    else:
        img = image_path_or_instance
        file_path = None

    info = {
        'width': img.width,
        'height': img.height,
        'dimensions': f"{img.width}x{img.height}",
        'aspect_ratio': round(img.width / img.height, 3),
        'color_mode': img.color_mode,
        'pixel_count': img.width * img.height,
        'memory_size': len(img._pixel_data),
    }

    if file_path:
        info.update({
            'file_name': os.path.basename(file_path),
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'file_extension': os.path.splitext(file_path)[1],
        })

    return info


def print_image_stats(image_path_or_instance):
    """
    打印图像统计信息

    参数:
        image_path_or_instance: 文件路径或WallowImage实例
    """
    info = get_image_info(image_path_or_instance)

    print("=" * 50)
    print("图像信息:")
    print("=" * 50)

    if 'file_name' in info:
        print(f"文件名: {info['file_name']}")
        print(f"路径: {info['file_path']}")
        print(f"文件大小: {_format_bytes(info['file_size'])}")

    print(f"尺寸: {info['dimensions']} 像素")
    print(f"纵横比: {info['aspect_ratio']}")
    print(f"像素数量: {info['pixel_count']:,}")
    print(f"颜色模式: {info['color_mode']}")
    print(f"内存占用: {_format_bytes(info['memory_size'])}")
    print("=" * 50)


def _format_bytes(bytes_value):
    """格式化字节数为人类可读格式"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024 or unit == 'GB':
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024
