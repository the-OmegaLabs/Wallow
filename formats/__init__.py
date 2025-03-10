from .base import ImageAIc
from .bmp import BMPAIc
from .png import PNGAIc
from .jpeg import JPEGAIc  # 添加JPEG编解码器
from .gif import GIFAIc    # 添加GIF编解码器

# 注册所有编解码器
_REGISTERED_CODECS = [
    BMPAIc(),
    PNGAIc(),
    JPEGAIc(),  # 添加JPEG编解码器
    GIFAIc(),   # 添加GIF编解码器
]


def get_codec(file_path=None, header=None):
    """智能获取匹配的编解码器"""
    # 优先通过文件头检测
    if header:
        for codec in _REGISTERED_CODECS:
            if codec.detect(header):
                return codec

    # 通过文件扩展名回退
    if file_path:
        ext = file_path.split('.')[-1].lower()
        for codec in _REGISTERED_CODECS:
            if ext in codec.supported_extensions:
                return codec

    raise ValueError("No compatible codec found")


__all__ = ['get_codec', 'ImageAIc', 'BMPAIc', 'PNGAIc', 'JPEGAIc', 'GIFAIc']
