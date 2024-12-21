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
from GUI.tab_log import LogTab
from GUI.tab_pretask import PreTaskTab
from GUI.icons.icons import Icons

from PIGEON.config import setting, windows_position, Config


# from PIGEON import Task
class MyTabView(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)
        self.configure(bg_color="#f3f3f3")
        self.configure(border_width=1)
        self.corner_radius = 1
        self.anchor("n")

        # create tabs
        self.add("常用")
        self.add("道馆")
        self.add("绘卷")
        self.add("调度器")
        self.add("设置")
        self.add("log")

        # create widgets on tabs
        self.maintab = MainTab(self.tab("常用"))
        self.settingtab = SettingTab(self.tab("设置"))
        self.dgtab = DgTab(self.tab("道馆"))
        self.tstab = TsTab(self.tab("绘卷"))
        self.logtab = LogTab(self.tab("log"))
        self.pretasktab = PreTaskTab(self.tab("调度器"))

        # add widgets on tabs
        self.maintab.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.settingtab.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.dgtab.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.tstab.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.logtab.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.pretasktab.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")


class log_area(ctk.CTkTextbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.tag_config("sep", foreground="#14bacc")  # 分割线标签
        self.tag_config("board", foreground="#87CEFA")  # 蓝色文本标签
        self.tag_config("content_info", foreground="#48BB31")  # 绿色文本标签
        self.tag_config("content_error", foreground="#FF0006")  # 红色文本标签
        self.tag_config("content_debug", foreground="#FFA500")  # 黄色文本标签
        self.tag_config("time", foreground="grey")  # 时间文本标签
        self.configure(fg_color="black", text_color="green", font=("微软雅黑", 12))
        self.Stop_auto_scroll = False
        self.bind("<Enter>", self.mouse_in_log_area)
        self.bind("<Leave>", self.mouse_out_log_area)

    def mouse_in_log_area(self, event):
        self.Stop_auto_scroll = True
        # print(f"{event}, mouse in log area")

    def mouse_out_log_area(self, event):
        self.Stop_auto_scroll = False
        # print(f"{event}, mouse out log area")

    def yview_moveto(self, fraction):
        if self.Stop_auto_scroll:
            return
        return super().yview_moveto(fraction)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        x, y = self.get_window_position()
        self.geometry(f"265x360+{x}+{y}")
        self.title("八尺琼勾玉")
        self.iconbitmap("GUI/icons/icon.ico")
        self.resizable(False, False)
        self.config(bg="#f3f3f3")
        ctk.set_default_color_theme("green")
        self.wm_attributes("-topmost", 1)  # 窗口置顶
        self.protocol("WM_DELETE_WINDOW", self.save_profile)  # 关闭窗口时执行save_profile函数

        self.tab_view = MyTabView(master=self, width=255, height=150, anchor="nw", command=self.tab_changed)
        self.tab_view.pack(side="top")

        self.log_area = log_area(master=self, width=260, bg_color="#f3f3f3")
        self.log_area.pack(side="bottom", fill="y", pady=2, expand=True)

        self.load_profile()  # 加载配置文件

    def tab_changed(self):
        tab_name = self.tab_view.get()
        # print(tab_name)
        if tab_name in ["调度器", "设置", "log"]:
            self.log_area.forget()
        else:
            self.log_area.pack(side="bottom", fill="y", expand=True)

    def save_profile(self):
        try:
            for key, value in ToggleButton.values.items():
                setting[key] = value.get()
        except:

            pass
        try:
            windows_position["x"] = self.winfo_x()
            windows_position["y"] = self.winfo_y()
        except:
            pass
        Config.save_all_config()
        self.destroy()

    def load_profile(self):
        for k, v in setting:
            ToggleButton.values[k].set(v)
        pass

    def get_window_position(self):
        try:
            return windows_position["x"], windows_position["y"]
        except FileNotFoundError:
            return 200, 200


if __name__ == "__main__":

    app = App()
    app.mainloop()
