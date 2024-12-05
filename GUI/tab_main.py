import customtkinter as ctk
from GUI.togglebuton import ToggleButton


class MainTab(ctk.CTkFrame):

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.grid_rowconfigure(3, weight=1)

        # create variables here
        self.times_value = ctk.StringVar()
        ToggleButton.values.update({"times": self.times_value})  # 绑定变量到ToggleButton类

        # add widgets here
        # buttons
        self.yh_btn = ToggleButton(self, text_off="御魂", name="御魂")
        self.ql_btn = ToggleButton(self, text_off="契灵", name="契灵")
        self.hd_btn = ToggleButton(self, text_off="智能", name="智能")
        self.tp_btn = ToggleButton(self, text_off="结界突破", name="结界突破")
        self.ltp_btn = ToggleButton(self, text_off="寮突破", name="寮突破")
        self.dg_btn = ToggleButton(self, text_off="道馆", name="道馆")
        # text
        self.text_times = ctk.CTkLabel(self, text="执行次数:", font=("微软雅黑", 14))
        # combobox
        self.times = ctk.CTkComboBox(self, values=["10", "30", "50", "100", "200", "300", "500", "999"], width=80, height=20, command=self.times_slider_value, justify="center", variable=self.times_value)
        self.times.set("30")  # set default value
        # slider
        self.times_slider = ctk.CTkSlider(self, from_=0, to=300, command=self.times_slider_value, number_of_steps=300)

        # add widgets to layout
        self.yh_btn.grid(row=0, column=0, padx=5, pady=2, sticky="ew")
        self.ql_btn.grid(row=0, column=1, padx=5, pady=0, sticky="ew")
        self.hd_btn.grid(row=0, column=2, padx=5, pady=2, sticky="ew")
        self.tp_btn.grid(row=1, column=0, padx=5, pady=2, sticky="ew")
        self.ltp_btn.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.dg_btn.grid(row=1, column=2, padx=5, pady=2, sticky="ew")

        self.text_times.grid(row=2, column=0, padx=5, pady=0, sticky="nsew")
        self.times.grid(row=2, column=1, columnspan=2, padx=5, pady=0, sticky="ew")
        self.times_slider.grid(row=3, column=0, columnspan=4, padx=5, pady=0, sticky="ew")

    # synchronize the values of times_value and times_slider
    def times_slider_value(self, value):
        # print(f"type of value is {type(value)}")
        if isinstance(value, str):
            self.times_slider.set(int(value))
            # print(f"set times_slider to: {value}")
        elif isinstance(value, float):
            self.times.set(int(value))
            # print(f"set times to: {value}")
