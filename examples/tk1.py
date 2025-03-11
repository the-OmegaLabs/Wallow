import tkinter as tk
from tkinter import messagebox
from core import WallowImage as wl
root = tk.Tk()
exampleImage = wl.open("./AC_Header_Gen4.jpg").to_tkinter_image()
imageBtn = tk.Label(root, image=exampleImage)
imageBtn.pack()
messagebox.showinfo("提示", "这是一个提示信息")
root.mainloop()