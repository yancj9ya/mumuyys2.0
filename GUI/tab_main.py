import customtkinter as ctk
from GUI.togglebuton import ToggleButton


class MainTab(ctk.CTkFrame):

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        # create variables here
        self.times_value = ctk.StringVar()
        ToggleButton.values.update({"times": self.times_value})  # 绑定变量到ToggleButton类
        # layout
        self.group0 = ctk.CTkFrame(self)
        self.line1 = ctk.CTkFrame(self.group0, fg_color="transparent")
        self.line2 = ctk.CTkFrame(self.group0, fg_color="transparent")
        self.group1 = ctk.CTkFrame(self)
        self.line3 = ctk.CTkFrame(self.group1, fg_color="transparent")
        self.line4 = ctk.CTkFrame(self.group1, fg_color="transparent")
        self.line5 = ctk.CTkFrame(self.group1, fg_color="transparent")

        # add widgets here
        # buttons
        self.yh_btn = ToggleButton(self.line3, text_off="御魂", name="御魂")
        self.yh_btn.pack(side="left", expand=True, padx=5, pady=5)
        self.ql_btn = ToggleButton(self.line3, text_off="契灵", name="契灵")
        self.ql_btn.pack(side="left", expand=True, padx=5, pady=5)
        self.hd_btn = ToggleButton(self.line3, text_off="智能", name="智能")
        self.hd_btn.pack(side="left", expand=True, padx=5, pady=5)
        self.tp_btn = ToggleButton(self.line4, text_off="结界突破", name="结界突破")
        self.tp_btn.pack(side="left", padx=7, pady=5)
        self.ltp_btn = ToggleButton(self.line4, text_off="寮突破", name="寮突破")
        self.ltp_btn.pack(side="left", expand=True, padx=5, pady=5)
        self.dg_btn = ToggleButton(self.line4, text_off="六道之门", name="六道之门")
        self.dg_btn.pack(side="left", expand=True, padx=5, pady=5)
        self.dg_btn = ToggleButton(self.line5, text_off="道馆", name="道馆")
        self.dg_btn.pack(side="left", padx=7, pady=5)
        # text
        self.text_times = ctk.CTkLabel(self.line1, text="执行次数:", font=("微软雅黑", 14))
        self.text_times.pack(side="left", fill="x", padx=1, pady=5, expand=True)
        # combobox
        self.times = ctk.CTkComboBox(self.line1, values=["10", "30", "50", "80", "500", "999"], width=80, height=25, command=self.times_slider_value, justify="center", variable=self.times_value)
        self.times.set("30")  # set default value
        self.times.pack(padx=15, pady=5, side="left", fill="x", expand=True)
        # slider
        self.times_slider = ctk.CTkSlider(self.line2, width=240, from_=0, to=300, command=self.times_slider_value, number_of_steps=300)
        self.times_slider.set(30)  # set default value
        self.times_slider.pack(padx=0, pady=5)

        # add widgets to layout
        self.line1.pack(fill="x")
        self.line2.pack(fill="x")
        self.line3.pack(fill="x")
        self.line4.pack(fill="x")
        self.line5.pack(fill="x")
        self.group0.pack(fill="x", pady=5, expand=True, anchor="n")
        self.group1.pack(fill="x", pady=5, expand=True, anchor="n")

    # synchronize the values of times_value and times_slider
    def times_slider_value(self, value):
        # print(f"type of value is {type(value)}")
        if isinstance(value, str):
            self.times_slider.set(int(value))
            # print(f"set times_slider to: {value}")
        elif isinstance(value, float):
            self.times.set(int(value))
            # print(f"set times to: {value}")
