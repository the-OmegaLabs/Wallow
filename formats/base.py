from abc import ABC, abstractmethod

from core import WallowImage


class ImageAIc(ABC):
    supported_extensions = []

    @staticmethod
    @abstractmethod
    def detect(header: bytes) -> bool:
        """通过文件头检测格式"""
        pass

    @abstractmethod
    def decode(self, file_path: str) -> 'WallowImage':
        pass

    @abstractmethod
    def encode(self, image: 'WallowImage', file_path: str, **options):
        pass


class BitmapCodec(ImageAIc):
    SUPPORTED_MODES = {'RGB', 'RGBA', 'L'}