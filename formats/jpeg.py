import struct
from io import BytesIO

try:
    from PIL import Image as PILImage

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from core import WallowImage
from .base import ImageAIc


class JPEGAIc(ImageAIc):
    supported_extensions = ['jpg', 'jpeg', 'jpe', 'jif', 'jfif']

    @staticmethod
    def detect(header):
        # JPEG文件头标识 (SOI marker)
        return header.startswith(b'\xFF\xD8\xFF')

    def decode(self, file_path):
        if not PIL_AVAILABLE:
            raise ImportError("PIL/Pillow library is required for JPEG support")

        with PILImage.open(file_path) as img:
            # 将PIL图像转换为RGB模式
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # 获取像素数据
            width, height = img.size
            pixel_data = bytearray(img.tobytes())

        return WallowImage(pixel_data, 'RGB', (width, height))

    def encode(self, pixel_data, color_mode, dimensions, output_path, quality=85):
        if not PIL_AVAILABLE:
            raise ImportError("PIL/Pillow library is required for JPEG support")

        width, height = dimensions

        # 创建PIL图像
        pil_img = PILImage.frombytes(
            color_mode,
            (width, height),
            bytes(pixel_data)
        )

        # 保存为JPEG
        pil_img.save(output_path, format='JPEG', quality=quality)
