from io import BytesIO

try:
    from PIL import Image as PILImage

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from core import WallowImage
from .base import ImageAIc


class GIFAIc(ImageAIc):
    supported_extensions = ['gif']

    @staticmethod
    def detect(header):
        # GIF文件头标识 (GIF87a 或 GIF89a)
        return (header.startswith(b'GIF87a') or
                header.startswith(b'GIF89a'))

    def decode(self, file_path):
        if not PIL_AVAILABLE:
            raise ImportError("PIL/Pillow library is required for GIF support")

        with PILImage.open(file_path) as img:
            # 获取第一帧（如果是动画GIF）
            if hasattr(img, 'n_frames') and img.n_frames > 1:
                print(f"Note: GIF contains {img.n_frames} frames. Only the first frame is loaded.")

            # 将PIL图像转换为RGB模式
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # 获取像素数据
            width, height = img.size
            pixel_data = bytearray(img.tobytes())

        return WallowImage(pixel_data, 'RGB', (width, height))

    def encode(self, pixel_data, color_mode, dimensions, output_path, quality=85):
        if not PIL_AVAILABLE:
            raise ImportError("PIL/Pillow library is required for GIF support")

        width, height = dimensions

        # 创建PIL图像
        pil_img = PILImage.frombytes(
            color_mode,
            (width, height),
            bytes(pixel_data)
        )

        # 保存为GIF
        pil_img.save(output_path, format='GIF')
