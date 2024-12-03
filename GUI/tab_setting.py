import customtkinter as ctk
from GUI.togglebuton import ToggleButton


class SettingTab(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        # create viriables
        self.keep_level_var = ctk.BooleanVar(value=True)
        self.set_window_top_var = ctk.IntVar(value=1)
        self.set_window_top_var.trace_add("write", self.set_window_top)
        self.ui_delay_var = ctk.DoubleVar(value=0.5)
        # 绑定变量到ToggleButton类
        ToggleButton.values.update({"tp_keep_level": self.keep_level_var, "ui_delay": self.ui_delay_var, "set_window_top": self.set_window_top_var})

        # create widgets
        self.keep_level_check = ctk.CTkSwitch(self, text="突破保级", variable=self.keep_level_var, onvalue=True, offvalue=False)
        self.set_window_top_check = ctk.CTkSwitch(self, text="置顶窗口", variable=self.set_window_top_var, onvalue=1, offvalue=0, command=self.set_window_top)

        self.ui_delay_slider = ctk.CTkSlider(
            self,
            from_=0.1,
            to=2,
            variable=self.ui_delay_var,
            orientation="vertical",
            height=300,
        )
        # add widgets to layout
        self.keep_level_check.grid(row=0, column=1, padx=10, pady=10)
        self.ui_delay_slider.grid(row=0, column=0, rowspan=10, padx=10, pady=10, sticky="w")
        self.set_window_top_check.grid(row=1, column=1, padx=10, pady=10)

    def set_window_top(self, *args):
        # print(args)
        self.master.master.master.wm_attributes("-topmost", self.set_window_top_var.get())
