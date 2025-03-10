import struct

from core import WallowImage
from .base import ImageCodec


class BMPCodec(ImageCodec):
    supported_extensions = ['bmp', 'dib']

    @staticmethod
    def detect(header):
        return header.startswith(b'BM')

    def decode(self, file_path):
        with open(file_path, 'rb') as f:
            header = f.read(54)
            width = struct.unpack('<I', header[18:22])
            height = struct.unpack('<I', header[22:26])

            # 跳转到像素数据起始位置
            f.seek(struct.unpack('<I', header[10:14]))
            pixel_data = f.read()

        return self._convert_bgr(pixel_data, width, height)

    def _convert_bgr(self, data, width, height):
        # 将BGR转换为RGB
        converted = bytearray()
        for i in range(0, len(data), 3):
            converted.extend([data[i + 2], data[i + 1], data[i]])
        return WallowImage(converted, 'RGB', (width, height))