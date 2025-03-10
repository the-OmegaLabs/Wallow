import tkinter as tk
from tkinter import filedialog


class TkPreview:
    @staticmethod
    def show_image(image_instance):
        global photo_data
        root = tk.Tk()
        root.title("Wallow Image Preview")

        canvas = tk.Canvas(root,
                           width=image_instance.width,
                           height=image_instance.height)
        canvas.pack()

        photo = tk.PhotoImage(
            width=image_instance.width,
            height=image_instance.height
        )

        # 转换颜色模式
        if image_instance.color_mode == 'RGB':
            photo_data = bytes(image_instance._pixel_data)
        elif image_instance.color_mode == 'RGBA':
            photo_data = bytes([v for i in range(0, len(image_instance._pixel_data), 4)
                                for v in image_instance._pixel_data[i:i + 3]])

        photo.put(photo_data, (0, 0, image_instance.width - 1, image_instance.height - 1))  # type: ignore

        canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        root.mainloop()