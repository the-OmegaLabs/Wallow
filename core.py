from abc import ABC, abstractmethod
import struct
import tkinter as tk


class ImageProcessor(ABC):
    @classmethod
    @abstractmethod
    def open(cls, file_path):
        pass

    @abstractmethod
    def apply_operation(self, operation, **params):
        pass


class WallowImage(ImageProcessor):
    def apply_operation(self, operation: str, **params) -> 'WallowImage':
        self._operation_stack.append((operation, params))
        return self

    def __init__(self, pixel_data, color_mode, dimensions):
        self._pixel_data = bytearray(pixel_data)
        self.color_mode = color_mode
        self.width, self.height = dimensions
        self._operation_stack = []

    @classmethod
    def open(cls, file_path):
        from formats import get_codec
        codec = get_codec(file_path)
        return codec.decode(file_path)

    def resize(self, new_width=None, new_height=None):
        self._operation_stack.append(('resize', {
            'width': new_width,
            'height': new_height
        }))
        return self

    def apply_filter(self, filter_func):
        self._operation_stack.append(('filter', {
            'func': filter_func
        }))
        return self

    def save(self, output_path, quality=85):
        from formats import get_codec
        processed_data = self._process_pipeline()
        get_codec(output_path).encode(
            processed_data,
            self.color_mode,
            (self.width, self.height),
            output_path,
            quality
        )

    def _process_pipeline(self):
        data = self._pixel_data
        for op_type, params in self._operation_stack:
            if op_type == 'resize':
                data = self._resize_impl(data, **params)
            elif op_type == 'filter':
                data = params['func'](data)
        return data

    def _resize_impl(self, data, width, height):
        # Nearest-neighbor缩放算法
        scale_x = width / self.width if width else 1.0
        scale_y = height / self.height if height else 1.0
        new_width = int(self.width * scale_x)
        new_height = int(self.height * scale_y)

        resized = bytearray(new_width * new_height * len(self.color_mode))
        for y in range(new_height):
            src_y = int(y / scale_y)
            for x in range(new_width):
                src_x = int(x / scale_x)
                src_pos = (src_y * self.width + src_x) * len(self.color_mode)
                dst_pos = (y * new_width + x) * len(self.color_mode)
                resized[dst_pos:dst_pos + 3] = data[src_pos:src_pos + 3]
        return resized

    def to_tkinter_image(self):
        if self.color_mode not in ('RGB', 'RGBA'):
            raise ValueError("Only RGB and RGBA color modes are supported for tkinter conversion")

        image = tk.PhotoImage(width=self.width, height=self.height)

        pixels = []
        bytes_per_pixel = len(self.color_mode)
        for i in range(0, len(self._pixel_data), bytes_per_pixel):
            r, g, b = self._pixel_data[i:i+3]
            hex_color = f'#{r:02x}{g:02x}{b:02x}'
            pixels.append(hex_color)

        image.put('{' + ' '.join(pixels) + '}', to=(0, 0, self.width, self.height))

        return image