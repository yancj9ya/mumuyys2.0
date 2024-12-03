import customtkinter as ctk
from GUI.togglebuton import ToggleButton
import os


class DgTab(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        # create viriables
        self.dg_xs = ctk.StringVar(value="1:4.6")
        self.dg_rs = ctk.IntVar(value=80)
        # 绑定变量到ToggleButton类
        ToggleButton.values.update({"dg_xs": self.dg_xs, "dg_rs": self.dg_rs})

        # create widgets
        self.xs = ctk.CTkLabel(self, text="进攻道馆系数：", font=("微软雅黑", 14))
        self.rs = ctk.CTkLabel(self, text="进攻道馆人数：", font=("微软雅黑", 14))
        self.xs_input = ctk.CTkEntry(self, textvariable=self.dg_xs, width=50, justify="center")
        self.rs_input = ctk.CTkEntry(self, textvariable=self.dg_rs, width=50, justify="center")
        self.open_awards_folder = ctk.CTkButton(self, width=70, text="统计文件夹", command=self.open_awards_folder_func)
        self.dg_btn = ToggleButton(self, text_off="开始道馆", name="dg_btn")

        # add widgets to layout
        self.xs.grid(row=0, column=0, padx=0, pady=5)
        self.rs.grid(row=1, column=0, padx=0, pady=5)
        self.xs_input.grid(row=0, column=1, padx=0, pady=5)
        self.rs_input.grid(row=1, column=1, padx=0, pady=5)
        self.open_awards_folder.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.dg_btn.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

    def open_awards_folder_func(self):
        folder_path = r"D:\\python\\mumuyys2.0\\task\dg\\awards"  # 请根据实际情况修改路径
        try:
            if os.path.exists(folder_path):
                os.startfile(folder_path)  # 打开文件夹
            else:
                raise FileNotFoundError("文件夹不存在。")
        except Exception as e:
            print(e)
            pass
