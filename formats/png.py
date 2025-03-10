import struct
import zlib
from io import BytesIO

from core import WallowImage
from .base import ImageAIc  # 使用ImageAIc作为基类


class PNGAIc(ImageAIc):  # 将PNG改名为PNGAIc
    supported_extensions = ['png']

    @staticmethod
    def detect(header):
        # PNG文件头标识
        return header.startswith(b'\x89PNG\r\n\x1a\n')

    def decode(self, file_path):
        with open(file_path, 'rb') as f:
            png_data = f.read()

        # 检查PNG签名
        if not self.detect(png_data[:8]):
            raise ValueError("Not a valid PNG file")

        # 解析IHDR块
        ihdr_data = png_data[16:29]
        width = struct.unpack('>I', ihdr_data[0:4])[0]
        height = struct.unpack('>I', ihdr_data[4:8])[0]
        bit_depth = ihdr_data[8]
        color_type = ihdr_data[9]

        # 目前仅支持RGB和RGBA格式
        if color_type == 2:  # RGB
            color_mode = 'RGB'
            bytes_per_pixel = 3
        elif color_type == 6:  # RGBA
            color_mode = 'RGBA'
            bytes_per_pixel = 4
        else:
            raise ValueError(f"Unsupported PNG color type: {color_type}")

        if bit_depth != 8:
            raise ValueError(f"Unsupported PNG bit depth: {bit_depth}")

        # 提取IDAT块并合并
        idat_data = bytearray()
        offset = 8  # 跳过PNG签名

        while offset < len(png_data):
            chunk_length = struct.unpack('>I', png_data[offset:offset + 4])[0]
            chunk_type = png_data[offset + 4:offset + 8]
            chunk_data = png_data[offset + 8:offset + 8 + chunk_length]

            if chunk_type == b'IDAT':
                idat_data.extend(chunk_data)
            elif chunk_type == b'IEND':
                break

            offset += 12 + chunk_length  # 跳到下一个块

        # 解压IDAT数据
        decompressed_data = zlib.decompress(idat_data)

        # 解析像素数据
        pixel_data = bytearray(width * height * bytes_per_pixel)
        stride = width * bytes_per_pixel + 1  # +1是因为每行前面有一个过滤类型字节

        for y in range(height):
            filter_type = decompressed_data[y * stride]
            row_start = y * width * bytes_per_pixel

            for x in range(width):
                src_pos = y * stride + 1 + x * bytes_per_pixel
                dst_pos = row_start + x * bytes_per_pixel

                # 复制像素数据（不进行过滤，简化实现）
                for i in range(bytes_per_pixel):
                    pixel_data[dst_pos + i] = decompressed_data[src_pos + i]

        return WallowImage(pixel_data, color_mode, (width, height))

    def encode(self, pixel_data, color_mode, dimensions, output_path):
        width, height = dimensions

        # PNG签名
        png_signature = b'\x89PNG\r\n\x1a\n'

        # IHDR块
        ihdr_chunk = bytearray(13)
        ihdr_chunk[0:4] = struct.pack('>I', width)
        ihdr_chunk[4:8] = struct.pack('>I', height)
        ihdr_chunk[8] = 8  # 位深度

        if color_mode == 'RGB':
            ihdr_chunk[9] = 2  # 颜色类型 (RGB)
            bytes_per_pixel = 3
        elif color_mode == 'RGBA':
            ihdr_chunk[9] = 6  # 颜色类型 (RGBA)
            bytes_per_pixel = 4
        else:
            raise ValueError(f"Unsupported color mode: {color_mode}")

        ihdr_chunk[10:13] = b'\x00\x00\x00'  # 压缩方法、过滤方法、隔行扫描方法

        # 创建IHDR块
        ihdr = self._create_chunk(b'IHDR', ihdr_chunk)

        # 准备像素数据以进行压缩
        raw_data = bytearray(height * (width * bytes_per_pixel + 1))

        for y in range(height):
            # 每行的第一个字节表示过滤类型（0表示无过滤）
            raw_data[y * (width * bytes_per_pixel + 1)] = 0

            for x in range(width):
                src_pos = (y * width + x) * bytes_per_pixel
                dst_pos = y * (width * bytes_per_pixel + 1) + 1 + x * bytes_per_pixel

                for i in range(bytes_per_pixel):
                    raw_data[dst_pos + i] = pixel_data[src_pos + i]

        # 压缩数据
        compressed_data = zlib.compress(raw_data)

        # 创建IDAT块
        idat = self._create_chunk(b'IDAT', compressed_data)

        # 创建IEND块
        iend = self._create_chunk(b'IEND', b'')

        # 写入PNG文件
        with open(output_path, 'wb') as f:
            f.write(png_signature)
            f.write(ihdr)
            f.write(idat)
            f.write(iend)

    def _create_chunk(self, chunk_type, data):
        """创建PNG块"""
        chunk = bytearray(len(data) + 12)
        chunk[0:4] = struct.pack('>I', len(data))
        chunk[4:8] = chunk_type
        chunk[8:8 + len(data)] = data

        # 计算CRC32
        crc = zlib.crc32(chunk_type)
        crc = zlib.crc32(data, crc) & 0xffffffff

        chunk[8 + len(data):] = struct.pack('>I', crc)
        return chunk
