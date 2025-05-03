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
        # layout
        self.group0 = ctk.CTkScrollableFrame(self, label_text="道馆设置", height=10)
        self.group0._scrollbar.configure(height=70, width=0)
        self.line1 = ctk.CTkFrame(self.group0, fg_color="transparent")
        self.line2 = ctk.CTkFrame(self.group0, fg_color="transparent")
        self.group1 = ctk.CTkFrame(self, height=40)
        # create widgets
        self.xs = ctk.CTkLabel(self.line1, text="进攻道馆系数范围：", font=("微软雅黑", 14))
        self.xs.pack(side="left")
        self.xs_input = ctk.CTkEntry(self.line1, textvariable=self.dg_xs, width=50, justify="center")
        self.xs_input.pack(side="left", expand=True, fill="x")

        self.rs = ctk.CTkLabel(self.line2, text="进攻道馆人数最低：", font=("微软雅黑", 14))
        self.rs.pack(side="left")
        self.rs_input = ctk.CTkEntry(self.line2, textvariable=self.dg_rs, width=50, justify="center")
        self.rs_input.pack(side="left", expand=True, fill="x")

        self.open_awards_folder = ctk.CTkButton(self.group1, width=70, text="统计文件夹", font=("微软雅黑", 14), command=self.open_awards_folder_func)
        self.open_awards_folder.pack(side="right", padx=20)
        self.dg_btn = ToggleButton(self.group1, text_off="开始道馆", name="道馆", font=("微软雅黑", 14))
        self.dg_btn.pack(side="left", padx=20, pady=20)

        # add widgets to layout
        self.group0.pack(fill="x", pady=2)
        self.line1.pack(fill="x", padx=10, pady=2)
        self.line2.pack(fill="x", padx=10, pady=2)
        self.group1.pack(fill="x", pady=10)

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
