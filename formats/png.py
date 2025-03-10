import struct
import zlib
from core import WallowImage


class PNGCodec:
    @staticmethod
    def decode(file_path):
        with open(file_path, 'rb') as f:
            assert f.read(8) == b'\x89PNG\r\n\x1a\n', "Invalid PNG signature"

            # 读取IHDR块
            while True:
                chunk = f.read(8)
                length, chunk_type = struct.unpack(">I4s", chunk)
                if chunk_type == b'IHDR':
                    width, height = struct.unpack(">II", f.read(8))
                    break

            # 解压IDAT数据
            idat_data = bytearray()
            while True:
                chunk = f.read(8)
                length, chunk_type = struct.unpack(">I4s", chunk)
                if chunk_type == b'IDAT':
                    idat_data += f.read(length)
                elif chunk_type == b'IEND':
                    break
                f.seek(4, 1)  # 跳过CRC

            raw_data = zlib.decompress(idat_data)
            return WallowImage(raw_data, 'RGBA', (width, height))