import customtkinter as ctk
from tkinter import filedialog
from windows import Windows
from PIL import Image, ImageTk
import cv2, subprocess
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
        self.geometry("1470x600")
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
        self.left_frame = ctk.CTkFrame(self, width=300, height=620)
        self.left_frame.grid(row=0, column=1, padx=0, pady=10, sticky="sn")

        # 截图按钮
        self.screen_shot_button = ctk.CTkButton(self.left_frame, text="截图", command=self.screen_shot)
        self.screen_shot_button.grid(row=3, column=1, padx=10, pady=10)
        # 保存按钮
        self.save_and_fmt_button = ctk.CTkButton(self.left_frame, text="保存图片", command=self.save_img)
        self.save_and_fmt_button.grid(row=3, column=2, padx=10, pady=10)
        # 文件夹路径输入框
        self.folder_path_entry = ctk.CTkEntry(self.left_frame, placeholder_text="请输入文件夹路径", width=260, justify="center")
        self.folder_path_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        # 选择文件夹按钮
        self.choese_folder_button = ctk.CTkButton(self.left_frame, text="选择文件夹", width=20, command=self.choose_folder)
        self.choese_folder_button.grid(row=1, column=3, padx=10, pady=10, sticky="w")

        # 图片名称输入框
        _name_var = ctk.StringVar()
        self.img_name = ctk.CTkEntry(self.left_frame, placeholder_text="请输入图片名称", textvariable=_name_var, width=260, justify="center")
        self.img_name.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        _name_var.trace_add("write", self.dyn_creat_info)

        # 框选坐标显示框
        self.rect_info = ctk.CTkEntry(self.left_frame, placeholder_text="矩形框坐标", width=250, justify="center")
        self.rect_info.grid(row=4, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        # 复制按钮
        self.copy_button = ctk.CTkButton(self.left_frame, width=20, text="copy", command=lambda: self.copy_to_clipboard(str(self.coordinates)))
        self.copy_button.grid(row=4, column=3, padx=10, pady=10, sticky="ew")

        # 图片信息显示框
        self.img_info = ctk.CTkEntry(self.left_frame, placeholder_text="图片信息", width=250, justify="center")
        self.img_info.grid(row=5, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        # 图片信息保存按钮
        self.img_info_save_btn = ctk.CTkButton(self.left_frame, width=20, text="image_info", command=lambda: self.write_to_file("image"))
        self.img_info_save_btn.grid(row=5, column=3, padx=10, pady=10, sticky="ew")

        # 页面信息显示框
        self.page_info = ctk.CTkEntry(self.left_frame, placeholder_text="page信息", width=250, justify="center")
        self.page_info.grid(row=6, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        # 页面信息保存按钮
        self.page_info_save_btn = ctk.CTkButton(self.left_frame, width=20, text="page_info", command=lambda: self.write_to_file("page"))
        self.page_info_save_btn.grid(row=6, column=3, padx=10, pady=10, sticky="ew")

        # 点击坐标显示框
        self.click_info = ctk.CTkEntry(self.left_frame, placeholder_text="点击坐标", width=250, justify="center")
        self.click_info.grid(row=7, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        # 点击坐标保存按钮
        self.click_info_save_btn = ctk.CTkButton(self.left_frame, width=20, text="click_info", command=lambda: self.write_to_file("coor"))
        self.click_info_save_btn.grid(row=7, column=3, padx=10, pady=10, sticky="ew")

        # log显示框
        self.log_box = ctk.CTkTextbox(self.left_frame, bg_color="#dadada", fg_color="#000000", text_color="#48BB31", width=120, height=220)
        self.log_box.grid(row=8, column=1, columnspan=3, padx=10, pady=10, sticky="nsew")

    def log_print(self, text):
        self.log_box.insert("end", f"{text}\n")
        self.log_box.update()
        self.log_box.see("end")

    def copy_to_clipboard(self, text):
        subprocess.run(["cmd", "/c", f"echo {text} | clip"], shell=True)
        self.log_print(f"复制坐标 {text} 到剪贴板")

    def choose_folder(self):
        current_dir = os.getcwd()  # 获取当前目录
        folder_path = filedialog.askdirectory(initialdir=current_dir)
        if folder_path:  # 如果选择了文件夹
            self.folder_path_entry.delete(0, "end")
            self.folder_path_entry.insert(0, folder_path)
            self.log_print(folder_path)

    @property
    def coordinates(self):
        x1, y1, x2, y2 = self.rect.values()
        return x1, y1, x2, y2

    @property
    def name(self):
        return self.img_name.get()

    @property
    def file_path(self):
        base_path = self.folder_path_entry.get()
        img_name = self.name
        # 检查文件名是否合法
        if not img_name or not img_name.strip():
            self.log_print("图片名称不能为空")
            return
        if not re.match(r"^[\w\-. ]+$", img_name):
            self.log_print("图片名称含有非法字符")
            return

        # 检查目录是否存在
        if not os.path.exists(base_path):
            self.log_print("保存路径不存在")
            return

        path = os.path.relpath(base_path, start=os.curdir) + "/" + img_name + ".bmp"  # 保存路径
        path = path.replace("\\", "/")  # 路径格式化

        return path

    def save_img(self):
        path = self.file_path
        if self.np_image is not None and any(self.rect.values()):  # 确保 np_image 和矩形框有效
            x1, y1, x2, y2 = self.coordinates
            # 检查裁剪框的有效性
            if not (0 <= x1 < x2 <= self.np_image.shape[1] and 0 <= y1 < y2 <= self.np_image.shape[0]):
                self.log_print("裁剪框的坐标无效")
                return
            try:
                cropped_image = self.np_image[y1 - 4 : y2 - 4, x1 - 4 : x2 - 4]
                cv2.imencode(".bmp", cropped_image)[1].tofile(path)
                self.log_print("保存成功")
            except Exception as e:
                self.log_print(f"保存图像时出错: {e}")

    def format_img(self, fmt_type):
        x1, y1, x2, y2 = self.coordinates
        match fmt_type:
            case "image":
                img_info = f"{self.name}=['{self.file_path}', [{x1-4}, {y1-4}, {x2-4}, {y2-4}], '{self.name}']"
            case "page":
                img_info = f"{self.name}=Page('{self.name}',['{self.file_path}', [{x1-4}, {y1-4}, {x2-4}, {y2-4}], '{self.name}'])"
            case "coor":
                img_info = f"{self.name}=({x1-4}, {y1-4}, {x2-4}, {y2-4})"
        return img_info
        pass

    def write_to_file(self, save_type):
        try:
            self.img_info = self.format_img(save_type)
            self.log_print(self.img_info)
            if self.img_info:
                if not os.path.exists(os.path.join(self.folder_path_entry.get(), "img_info_auto_create.py")):
                    with open(os.path.join(self.folder_path_entry.get(), "img_info_auto_create.py"), "w") as file:
                        file.write(f"# this file is auto created by devtool at {datetime.now()}\n\n")  # 写入内容
                        self.log_print("创建文件成功")

                with open(os.path.join(self.folder_path_entry.get(), "img_info_auto_create.py"), "a") as f:
                    f.write(str(self.img_info) + "\n")  # 写入内容
                    self.log_print("写入文件成功")
            else:
                self.log_print("没有图像信息或图像名称")
        except Exception as e:
            self.log_print(f"写入文件时出错: {e}")

    def screen_shot(self):
        self.log_print("截图")
        try:
            self.np_image = self.windows.screenshot(self.windows.child_handle, [0, 0, 1280, 720])  # 截图函数
            pil_image = Image.fromarray(cv2.cvtColor(self.np_image, cv2.COLOR_BGR2RGB))
            self.current_image = ImageTk.PhotoImage(pil_image)
            self.screen_canvas.create_image(4, 4, anchor="nw", image=self.current_image)
        except Exception as e:
            self.log_print(f"截图时出错: {e}")

    def in_canvas(self, event):
        self.mouse_is_in_canvas = True
        # self.log_print("鼠标进入画布")

    def out_canvas(self, event):
        self.mouse_is_in_canvas = False
        # self.log_print("鼠标离开画布")

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
            self.log_print(f"矩形框坐标：{self.rect}")
            self.dyn_creat_info()

    def dyn_creat_info(self, *args, **kwargs):
        self.rect_info.delete(0, "end")
        self.rect_info.insert(0, f"{self.coordinates}")
        self.img_info.delete(0, "end")
        self.img_info.insert(0, f"{self.format_img('image')}")
        self.page_info.delete(0, "end")
        self.page_info.insert(0, f"{self.format_img('page')}")
        self.click_info.delete(0, "end")
        self.click_info.insert(0, f"{self.format_img('coor')}")

    def draw_rectangle(self):
        self.screen_canvas.delete("rect")
        self.screen_canvas.create_rectangle(self.rect["x1"], self.rect["y1"], self.rect["x2"], self.rect["y2"], outline="red", tags="rect")


if __name__ == "__main__":
    app = DevTool()
    app.mainloop()
