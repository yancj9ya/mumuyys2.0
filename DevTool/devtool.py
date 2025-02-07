import customtkinter as ctk
from tkinter import filedialog
from windows import Windows
from PIL import Image, ImageTk
import cv2
import os
import re
from datetime import datetime


class DevTool(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.windows = Windows()  # 初始化用于截图
        self.np_image = None  # 截图的 NumPy 图像
        self.current_image = None  # 当前显示的图像
        self.rect = {"x1": 0, "y1": 0, "x2": 0, "y2": 0}  # 矩形框
        self.img_info = None  # 保存图片信息
        # 创建窗口
        self.geometry("1470x700")
        self.title("DevTool")
        self.resizable(False, False)

        self.screen_canvas = ctk.CTkCanvas(self, width=1280, height=720)
        self.screen_canvas.configure(borderwidth=2, relief="solid")
        self.screen_canvas.bind("<Enter>", self.in_canvas)
        self.screen_canvas.bind("<Leave>", self.out_canvas)
        self.screen_canvas.bind("<Button-1>", self.on_click)
        self.screen_canvas.bind("<B1-Motion>", self.on_move)
        self.screen_canvas.bind("<ButtonRelease-1>", self.on_release)
        self.mouse_is_in_canvas = False
        # 画布
        self.screen_canvas.grid(row=0, column=0, padx=10, pady=10)
        # 左框架
        self.left_frame = ctk.CTkFrame(self, width=300, height=800)
        self.left_frame.grid(row=0, column=1, padx=0, pady=10, sticky="sn")
        # 截图按钮
        self.screen_shot_button = ctk.CTkButton(self.left_frame, text="截图", command=self.screen_shot)
        self.screen_shot_button.grid(row=3, column=1, padx=10, pady=10)
        # 保存并格式化按钮
        self.save_and_fmt_button = ctk.CTkButton(self.left_frame, text="保存并格式化", command=self.save_and_fmt)
        self.save_and_fmt_button.grid(row=3, column=2, padx=10, pady=10)
        # 文件夹路径输入框
        self.folder_path_entry = ctk.CTkEntry(self.left_frame, placeholder_text="请输入文件夹路径", width=260, justify="center")
        self.folder_path_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        # 选择文件夹按钮
        self.choese_folder_button = ctk.CTkButton(self.left_frame, text="选择文件夹", width=10, command=self.choose_folder)
        self.choese_folder_button.grid(row=1, column=3, padx=10, pady=10)
        # 图片名称输入框
        self.img_name = ctk.CTkEntry(self.left_frame, placeholder_text="请输入图片名称", width=260, justify="center")
        self.img_name.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        # 框选坐标显示框
        self.rect_info = ctk.CTkEntry(self.left_frame, placeholder_text="矩形框坐标", width=260, justify="center")
        self.rect_info.grid(row=4, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

    def choose_folder(self):
        current_dir = os.getcwd()  # 获取当前目录
        folder_path = filedialog.askdirectory(initialdir=current_dir)
        if folder_path:  # 如果选择了文件夹
            self.folder_path_entry.delete(0, "end")
            self.folder_path_entry.insert(0, folder_path)
            print(folder_path)

    def save_and_fmt(self):
        base_path = self.folder_path_entry.get()
        img_name = self.img_name.get()

        # 检查文件名是否合法
        if not img_name or not img_name.strip():
            print("图片名称不能为空")
            return
        if not re.match(r"^[\w\-. ]+$", img_name):
            print("图片名称含有非法字符")
            return

        # 检查目录是否存在
        if not os.path.exists(base_path):
            print("保存路径不存在")
            return

        path = os.path.relpath(base_path, start=os.curdir) + "/" + img_name + ".bmp"  # 保存路径
        path = path.replace("\\", "/")  # 路径格式化
        if self.np_image is not None and any(self.rect.values()):  # 确保 np_image 和矩形框有效
            x1, y1, x2, y2 = self.rect.values()

            # 检查裁剪框的有效性
            if not (0 <= x1 < x2 <= self.np_image.shape[1] and 0 <= y1 < y2 <= self.np_image.shape[0]):
                print("裁剪框的坐标无效")
                return

            try:
                cropped_image = self.np_image[y1 - 4 : y2 - 4, x1 - 4 : x2 - 4]
                cv2.imencode(".bmp", cropped_image)[1].tofile(path)
                print("保存并格式化成功")
                ### page-format:::f"{img_name}=Page('{img_name}',['{path}', [{x1-4}, {y1-4}, {x2-4}, {y2-4}], '{img_name}'])"
                self.img_info = f"{img_name}=['{path}', [{x1-4}, {y1-4}, {x2-4}, {y2-4}], '{img_name}']"
                print(self.img_info)
                if self.img_info:
                    if not os.path.exists(os.path.join(self.folder_path_entry.get(), "img_info_auto_create.py")):
                        with open(os.path.join(self.folder_path_entry.get(), "img_info_auto_create.py"), "w") as file:
                            file.write(f"# this file is auto created by devtool at {datetime.now()}\n\n")  # 写入内容
                    with open(os.path.join(self.folder_path_entry.get(), "img_info_auto_create.py"), "a") as f:
                        f.write(str(self.img_info) + "\n")

                else:
                    print("没有图像信息或图像名称")
            except Exception as e:
                print(f"保存图像时出错: {e}")

    def write_to_file(self):
        if self.img_info:
            try:
                with open(os.path.join(self.folder_path_entry.get(), "img_info_auto_create.py"), "a") as f:
                    f.write(str(self.img_info) + "\n")
            except Exception as e:
                print(f"写入文件时出错: {e}")
        else:
            print("没有图像信息或图像名称")

    def screen_shot(self):
        print("截图")
        try:
            self.np_image = self.windows.screenshot(self.windows.child_handle, [0, 0, 1280, 720])  # 截图函数
            pil_image = Image.fromarray(cv2.cvtColor(self.np_image, cv2.COLOR_BGR2RGB))
            self.current_image = ImageTk.PhotoImage(pil_image)
            self.screen_canvas.create_image(4, 4, anchor="nw", image=self.current_image)
        except Exception as e:
            print(f"截图时出错: {e}")

    def in_canvas(self, event):
        self.mouse_is_in_canvas = True
        # print("鼠标进入画布")

    def out_canvas(self, event):
        self.mouse_is_in_canvas = False
        # print("鼠标离开画布")

    def on_click(self, event):
        if self.mouse_is_in_canvas:
            self.rect["x1"] = event.x
            self.rect["y1"] = event.y

    def on_move(self, event):
        if self.mouse_is_in_canvas:
            self.rect["x2"] = event.x
            self.rect["y2"] = event.y
            self.draw_rectangle()

    def on_release(self, event):
        if self.mouse_is_in_canvas:
            self.rect["x2"] = event.x
            self.rect["y2"] = event.y
            self.draw_rectangle()
            print("矩形框坐标：", self.rect)
            self.rect_info.delete(0, "end")
            self.rect_info.insert(0, f"({self.rect['x1']}, {self.rect['y1']}, {self.rect['x2']}, {self.rect['y2']})")

    def draw_rectangle(self):
        self.screen_canvas.delete("rect")
        self.screen_canvas.create_rectangle(self.rect["x1"], self.rect["y1"], self.rect["x2"], self.rect["y2"], outline="red", tags="rect")


if __name__ == "__main__":
    app = DevTool()
    app.mainloop()
