import struct
from io import BytesIO

from core import WallowImage
from .base import ImageAIc  # 使用ImageAIc作为基类


class BMPAIc(ImageAIc):  # 将BMP改名为BMPAIc
    supported_extensions = ['bmp']

    @staticmethod
    def detect(header):
        # BMP文件头标识
        return header.startswith(b'BM')

    def decode(self, file_path):
        with open(file_path, 'rb') as f:
            bmp_data = f.read()

        # 读取头信息
        header_size = struct.unpack('<I', bmp_data[14:18])[0]
        width = struct.unpack('<i', bmp_data[18:22])[0]
        height = struct.unpack('<i', bmp_data[22:26])[0]
        bpp = struct.unpack('<H', bmp_data[28:30])[0]

        if bpp != 24 and bpp != 32:
            raise ValueError(f"Unsupported BMP bit depth: {bpp}")

        # 像素数据偏移位置
        pixel_offset = struct.unpack('<I', bmp_data[10:14])[0]

        # 读取像素数据
        pixel_data = bytearray()

        # 确定颜色模式
        if bpp == 24:
            color_mode = 'RGB'
        else:  # bpp == 32
            color_mode = 'RGBA'

        # BMP像素数据是从下到上存储的
        row_size = width * (bpp // 8)
        padding = (4 - (row_size % 4)) % 4  # 每行需要填充到4字节的倍数

        for y in range(height - 1, -1, -1):
            row_start = pixel_offset + y * (row_size + padding)
            row_end = row_start + row_size
            row_data = bmp_data[row_start:row_end]

            # 在BMP中，RGB顺序是BGR
            for i in range(0, len(row_data), bpp // 8):
                if bpp == 24:  # RGB
                    b, g, r = row_data[i:i + 3]
                    pixel_data.extend([r, g, b])
                else:  # RGBA
                    b, g, r, a = row_data[i:i + 4]
                    pixel_data.extend([r, g, b, a])

        return WallowImage(pixel_data, color_mode, (width, height))

    def encode(self, pixel_data, color_mode, dimensions, output_path):
        width, height = dimensions

        # BMP文件头（14字节）
        bmp_header = bytearray(14)
        bmp_header[0:2] = b'BM'  # 标识

        # DIB头信息（40字节 - BITMAPINFOHEADER）
        dib_header = bytearray(40)
        dib_header[0:4] = struct.pack('<I', 40)  # 头大小
        dib_header[4:8] = struct.pack('<i', width)  # 宽度
        dib_header[8:12] = struct.pack('<i', height)  # 高度
        dib_header[12:14] = struct.pack('<H', 1)  # 色彩平面数

        if color_mode == 'RGB':
            bytes_per_pixel = 3
            dib_header[14:16] = struct.pack('<H', 24)  # 每像素位数
        elif color_mode == 'RGBA':
            bytes_per_pixel = 4
            dib_header[14:16] = struct.pack('<H', 32)  # 每像素位数
        else:
            raise ValueError(f"Unsupported color mode: {color_mode}")

        row_size = width * bytes_per_pixel
        padding = (4 - (row_size % 4)) % 4  # 每行填充至4字节的倍数
        padded_row_size = row_size + padding

        # 像素数据大小
        pixel_array_size = padded_row_size * height

        # 像素数据偏移
        pixel_offset = 14 + 40  # 文件头 + DIB头

        # 文件总大小
        file_size = pixel_offset + pixel_array_size

        # 填充头信息
        bmp_header[2:6] = struct.pack('<I', file_size)  # 文件大小
        bmp_header[10:14] = struct.pack('<I', pixel_offset)  # 像素偏移

        # 创建像素数组
        pixel_array = bytearray(pixel_array_size)

        # 填充像素数据（从下到上）
        for y in range(height - 1, -1, -1):
            row_start = (height - 1 - y) * width * bytes_per_pixel
            for x in range(width):
                pixel_pos = row_start + x * bytes_per_pixel
                array_pos = y * padded_row_size + x * bytes_per_pixel

                if color_mode == 'RGB':
                    r, g, b = pixel_data[pixel_pos:pixel_pos + 3]
                    pixel_array[array_pos:array_pos + 3] = bytes([b, g, r])
                else:  # RGBA
                    r, g, b, a = pixel_data[pixel_pos:pixel_pos + 4]
                    pixel_array[array_pos:array_pos + 4] = bytes([b, g, r, a])

        # 写入文件
        with open(output_path, 'wb') as f:
            f.write(bmp_header)
            f.write(dib_header)
            f.write(pixel_array)
