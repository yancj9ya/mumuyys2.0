import customtkinter as ctk
from GUI.togglebuton import ToggleButton
from PIGEON.log import Log_to_file
import os


class LogTab(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        # create variables
        self.file_log = ctk.BooleanVar(value=False)
        self.file_log.trace_add("write", self.switch_file_log)  # 绑定变量到函数
        # 绑定变量到ToggleButton类
        ToggleButton.values.update({"file_log": self.file_log})
        # Create widgets
        # 顶部水平排列
        self.line1 = ctk.CTkFrame(self, corner_radius=5)
        self.file_log_switch = ctk.CTkSwitch(self.line1, text="写入文件", width=100, height=20, variable=self.file_log, command=self.switch_file_log)
        self.open_log_file = ctk.CTkButton(self.line1, width=70, text="log.txt", command=self.open_log_file_func, corner_radius=5)
        # add widgets to layout
        self.file_log_switch.pack(side="left", padx=10, expand=True)
        self.open_log_file.pack(side="right", padx=2, pady=1, expand=True)
        self.line1.pack(fill="x", pady=0, ipady=2)

    def switch_file_log(self, *args, **kwargs):
        Log_to_file.is_open = self.file_log.get()
        # print(f"file log switch:{Log_to_file.is_open}")
        pass

    def open_log_file_func(self):
        file_path = r"log\\log.txt"  # 请根据实际情况修改路径
        try:
            if os.path.exists(file_path):
                os.startfile(file_path)  # 打开文件夹
            else:
                raise FileNotFoundError("文件夹不存在。")
        except Exception as e:
            print(e)
            pass

        pass
