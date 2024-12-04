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
        self.ui_delay_combox = ctk.CTkComboBox(self, values=["0.2", "0.5", "0.7"], justify="center", variable=self.ui_delay_var, width=10, height=20, command=self.ui_delay_slider_value)
        self.ui_delay_combox.set("0.5")
        self.ui_delay_slider = ctk.CTkSlider(
            self,
            from_=0.1,
            to=1,
            number_of_steps=20,
            orientation="horizontal",
            width=120,
            command=self.ui_delay_slider_value,
        )

        # add widgets to layout
        self.ui_delay_combox.grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky="ew")
        self.keep_level_check.grid(row=1, column=1, padx=0, pady=2)
        self.ui_delay_slider.grid(row=0, column=2, columnspan=3, padx=0, pady=0, sticky="w")
        self.set_window_top_check.grid(row=1, column=2, padx=0, pady=2)

    def set_window_top(self, *args):
        # print(args)
        self.master.master.master.wm_attributes("-topmost", self.set_window_top_var.get())

    # synchronize the values of times_value and times_slider
    def ui_delay_slider_value(self, value):
        # print(f"type of value is {type(value)}")
        if isinstance(value, str):
            self.ui_delay_slider.set(float(value))
            # print(f"set times_slider to: {value}")
        elif isinstance(value, float):
            self.ui_delay_combox.set(value)
            # print(f"set times to: {value}")
