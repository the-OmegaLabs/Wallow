from .base import ImageCodec
from .bmp import BMPCodec
from .png import PNGCodec

# 注册所有编解码器
_REGISTERED_CODECS = [
    BMPCodec(),
    PNGCodec(),
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


__all__ = ['get_codec', 'ImageCodec']