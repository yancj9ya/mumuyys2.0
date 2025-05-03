if __name__ == "__main__":
    import sys

    sys.path.append(r"D:\\python\\mumuyys2.0")
# this file is used to run the GUI program
import customtkinter as ctk
import tkinter.messagebox as messagebox
import json
from GUI.togglebuton import ToggleButton
from GUI.tab_main import MainTab
from GUI.tab_setting import SettingTab
from GUI.tab_dg import DgTab
from GUI.tab_ts import TsTab
from GUI.tab_log import LogTab
from GUI.tab_pretask import PreTaskTab
from GUI.stray import Pystray
from PIGEON.log import log
from PIGEON.config import setting, Config


# from PIGEON import Task
class MyTabView(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg_color="#f3f3f3")
        self.configure(border_width=0)
        self.corner_radius = 1

        # create tabs
        self.add("调度器")
        self.add("日志")
        self.add("常用")
        self.add("道馆")
        self.add("绘卷")
        self.add("设置")

        # create widgets on tabs
        self.maintab = MainTab(self.tab("常用"))
        self.settingtab = SettingTab(self.tab("设置"))
        self.dgtab = DgTab(self.tab("道馆"))
        self.tstab = TsTab(self.tab("绘卷"))
        self.logtab = LogTab(self.tab("日志"))
        self.pretasktab = PreTaskTab(self.tab("调度器"))

        # add widgets on tabs
        self.maintab.pack(side="top", fill="both", pady=0, expand=True)
        self.settingtab.pack(side="top", fill="both", pady=0, expand=True)
        self.dgtab.pack(side="top", fill="both", pady=0, expand=True)
        self.tstab.pack(side="top", fill="both", pady=0, expand=True)
        self.logtab.pack(side="top", fill="both", pady=0, expand=True)
        self.pretasktab.pack(side="top", fill="both", pady=0, expand=True)

        self.log_area = log_area(master=self.logtab)
        self.log_area.pack(side="bottom", fill="both", pady=0, expand=True)


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
        self._y_scrollbar.configure(width=2)

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
        # 初始化一个stray类
        self.stray = Pystray("GUI/icons/icon.ico", "PIGEON")
        self.stray.left_click = self.show_window  # 左键单击事件
        self.stray.left_doubleclick = self.hide_window  # 右键双击事件
        self.stray.menu = {
            1024: ("显示窗口", lambda: self.show_window()),
            1023: ("隐藏窗口", lambda: self.hide_window()),
            1025: ("退出", lambda: self.close_window()),
        }
        self.stray.run_detached()  # 后台运行stray
        x, y = self.get_window_position()
        self.geometry(f"265x360+{x}+{y}")
        self.title("牛马小纸人 v2.1")
        self.iconbitmap("GUI/icons/icon.ico")
        self.resizable(False, False)
        self.config(bg="#f3f3f3")
        ctk.set_default_color_theme("green")
        self.wm_attributes("-topmost", 1)  # 窗口置顶
        self.protocol("WM_DELETE_WINDOW", self.hide_window)  # 关闭窗口时执行save_profile函数

        self.tab_view = MyTabView(master=self, command=self.tab_changed)
        self.tab_view.pack(side="top", fill="both", padx=1, expand=True)

        # self.log_area = log_area(master=self, width=260, bg_color="#f3f3f3")
        # self.log_area.pack(side="bottom", fill="y", pady=2, expand=True)

        self.load_profile()  # 加载配置文件

    def tab_changed(self):
        tab_name = self.tab_view.get()
        print(tab_name)
        # if tab_name in ["调度器", "设置", "log"]:
        #     self.log_area.forget()
        # else:
        #     self.log_area.pack(side="bottom", fill="y", expand=True)

    def hide_window(self):
        self.withdraw()

    def show_window(self):

        self.deiconify()

    def close_window(self):
        # close_or_not = messagebox.askyesno("提示", "是否要退出程序？")
        # if close_or_not:
        self.save_profile()
        self.destroy()

    def save_profile(self):
        try:
            for key, value in ToggleButton.values.items():
                setting[key] = value.get()
            # save window position to config file
            setting["window_position"] = {"x": self.winfo_x(), "y": self.winfo_y()}
        except Exception as e:
            log.error(f"save_profile error: {e}")
            pass

        Config.save_all_config()

    def load_profile(self):
        for k, v in setting:
            if k == "window_position":
                continue
            if k in ToggleButton.values:
                ToggleButton.values[k].set(v)
        pass

    def get_window_position(self):
        try:
            return setting["window_position"]["x"], setting["window_position"]["y"]
        except Exception:
            return 200, 200


if __name__ == "__main__":

    app = App()
    app.mainloop()
