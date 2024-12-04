if __name__ == "__main__":
    import sys

    sys.path.append(r"D:\\python\\mumuyys2.0")
# this file is used to run the GUI program
import customtkinter as ctk
import json
from GUI.togglebuton import ToggleButton
from GUI.tab_main import MainTab
from GUI.tab_setting import SettingTab
from GUI.tab_dg import DgTab
from GUI.tab_ts import TsTab


# from PIGEON import Task
class MyTabView(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)
        self.configure(bg_color="#f3f3f3")
        self.configure(border_width=1)
        self.corner_radius = 1
        # self.configure(fg_color="grey")
        self.anchor("n")

        # create tabs
        self.add("常用")
        self.add("道馆")
        self.add("绘卷")
        self.add("其他")
        self.add("设置")
        self.add("log")

        # create widgets on tabs
        self.maintab = MainTab(self.tab("常用"))
        self.settingtab = SettingTab(self.tab("设置"))
        self.dgtab = DgTab(self.tab("道馆"))
        self.tstab = TsTab(self.tab("绘卷"))

        # add widgets on tabs
        self.maintab.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.settingtab.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.dgtab.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.tstab.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")


class log_area(ctk.CTkTextbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.tag_config("blue_text", foreground="#87CEFA")  # 蓝色文本标签
        self.tag_config("green_text", foreground="green")  # 绿色文本标签
        self.configure(fg_color="#000000", text_color="green", font=("微软雅黑", 12))


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        x, y = self.get_window_position()
        self.geometry(f"265x360+{x}+{y}")
        self.title("八尺琼勾玉")
        self.iconbitmap("GUI/icon.ico")
        self.resizable(False, False)
        self.config(bg="#f3f3f3")
        self.wm_attributes("-topmost", 1)  # 窗口置顶
        self.protocol("WM_DELETE_WINDOW", self.save_profile)  # 关闭窗口时执行save_profile函数

        self.tab_view = MyTabView(master=self, width=255, height=50, anchor="nw", command=self.tab_changed)
        self.tab_view.pack(side="top", fill="y")

        self.log_area = log_area(master=self, width=255, height=180, bg_color="#f3f3f3")
        self.log_area.pack(side="bottom", fill="y", expand=True)

        self.load_profile()  # 加载配置文件

    def tab_changed(self):
        tab_name = self.tab_view.get()
        # print(tab_name)
        if tab_name in ["其他", "设置"]:
            self.log_area.forget()
        else:
            self.log_area.pack(side="bottom", fill="y", expand=True)

    def save_profile(self):
        with open("GUI/profile.json", "w") as f:
            f.write(json.dumps({k: v.get() for k, v in ToggleButton.values.items()}))
        with open("GUI/window_position.json", "w") as f:
            f.write(json.dumps({"x": self.winfo_x(), "y": self.winfo_y()}))
        self.destroy()

    def load_profile(self):
        with open("GUI/profile.json", "r") as f:
            profile = json.loads(f.read())
        for k, v in profile.items():
            ToggleButton.values[k].set(v)
        pass

    def get_window_position(self):
        try:
            with open("GUI/window_position.json", "r") as f:
                position = json.loads(f.read())
            return position["x"], position["y"]
        except FileNotFoundError:
            return 200, 200


if __name__ == "__main__":

    app = App()
    app.mainloop()
