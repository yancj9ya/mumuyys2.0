import customtkinter as ctk
import json
import tkinter.messagebox as messagebox
from PIGEON.config import task_option
from PIGEON.log import log


class single_task(ctk.CTkFrame):
    def __init__(self, master, name, add_func, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.add_func = add_func
        self.grid_rowconfigure(0, minsize=30)
        self.grid_columnconfigure(0, minsize=120)
        # self.grid_columnconfigure(1, minsize=200)
        self._task = ctk.CTkButton(self, border_width=1, border_color="green", text=name, font=("微软雅黑", 12), width=5, corner_radius=2, command=self.add_func_wrapper)
        self.name = name
        self._task.grid(row=0, column=0, padx=2, pady=0, sticky="ew")

    def add_func_wrapper(self):
        return self.add_func(self.name)


class TaskLib(ctk.CTkToplevel):
    def __init__(self, window_pos, add_task_func, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_task_func = add_task_func
        self.main_window_pos = window_pos
        self.geometry("260x300+{}+{}".format(self.main_window_pos.winfo_x() - 330, self.main_window_pos.winfo_y()))
        self.title(f"任务库")
        self.update_idletasks()  # 刷新窗口
        self.resizable(False, True)
        self.task_frame = ctk.CTkScrollableFrame(self, width=228, height=340, corner_radius=2, label_text="任务列表")
        self.task_frame.pack(side="top", fill="both", expand=True)
        self.create_task_list()
        self.wm_attributes("-topmost", 1)  # 窗口置顶

    def create_task_list(self):
        # 确保父容器填充且可扩展
        self.task_frame.pack(fill="both", expand=True)  # 修改父容器布局

        # 清空原有内容（如果需重复生成列表）
        for widget in self.task_frame.winfo_children():
            widget.destroy()

        # 创建两列布局
        for i, task_name in enumerate(task_option.json.keys()):
            row = i // 2  # 每行两列，计算行号
            column = i % 2  # 列号 0 或 1
            # 创建单个任务
            task = single_task(self.task_frame, task_name, self.add_task_func)
            match task_name:
                case "自动关机":
                    task._task.configure(fg_color="lightblue")
            task.grid(row=row, column=column, sticky="n", pady=2, padx=2)  # 横向填充  # 添加列间距

        # 配置等宽列
        self.task_frame.columnconfigure(0, weight=1)
        self.task_frame.columnconfigure(1, weight=1)
