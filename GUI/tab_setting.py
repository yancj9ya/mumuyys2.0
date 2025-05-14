import customtkinter as ctk
from GUI.togglebuton import ToggleButton
from GUI.tab_dg import DgTab
from threading import Thread, Event
from task import Xz


class SettingTab(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.event = Event()
        # create viriables
        self.Guard_process_var = ctk.BooleanVar(value=True)
        self.Guard_process_var.trace_add("write", self.Guard_process)
        self.keep_level_var = ctk.BooleanVar(value=True)
        self.set_window_top_var = ctk.IntVar(value=1)
        self.set_window_top_var.trace_add("write", self.set_window_top)
        self.ui_delay_var = ctk.DoubleVar(value=0.5)
        # 绑定变量到ToggleButton类
        ToggleButton.values.update(
            {
                "tp_keep_level": self.keep_level_var,
                "ui_delay": self.ui_delay_var,
                "set_window_top": self.set_window_top_var,
                "cooperation_mission": self.Guard_process_var,
            }
        )

        # create layout
        self.group0 = ctk.CTkScrollableFrame(self, label_text="Setting", height=300, label_font=("Arial", 16, "bold"))
        self.group0._scrollbar.configure(width=10)
        self.group0.pack(fill="both", pady=0)
        self.group1 = ctk.CTkFrame(self.group0, fg_color="transparent")
        self.group1.pack(pady=1)
        self.line1 = ctk.CTkFrame(self.group1, fg_color="transparent")
        self.line1.pack(fill="x", pady=1)
        self.line2 = ctk.CTkFrame(self.group1, fg_color="transparent")
        self.line2.pack(fill="x", pady=1)
        self.line3 = ctk.CTkFrame(self.group1, fg_color="transparent")
        self.line3.pack(fill="x", pady=1)

        # create dg_setting
        self.dg_setting = DgTab(self.group0, width=240)
        self.dg_setting.pack(side="left", fill="x", padx=5, pady=1, expand=True)

        # create widgets
        self.cooperation_mission = ctk.CTkSwitch(self.line2, text="协助邀请", variable=self.Guard_process_var, onvalue=True, offvalue=False)
        self.cooperation_mission.pack(side="left", padx=2)

        self.keep_level_check = ctk.CTkSwitch(self.line2, text="突破保级", variable=self.keep_level_var, onvalue=True, offvalue=False)
        self.keep_level_check.pack(side="left", padx=2, expand=True)

        self.set_window_top_check = ctk.CTkSwitch(self.line3, text="置顶窗口", variable=self.set_window_top_var, onvalue=1, offvalue=0, command=self.set_window_top)
        self.set_window_top_check.pack(side="left", padx=2)

        self.ui_delay_combox = ctk.CTkComboBox(self.line1, values=["0.2", "0.5", "0.7"], width=80, justify="center", variable=self.ui_delay_var, height=20, command=self.ui_delay_slider_value)
        self.ui_delay_combox.set("0.5")
        self.ui_delay_combox.pack(side="left", padx=2, pady=5)

        self.ui_delay_slider = ctk.CTkSlider(self.line1, from_=0.1, to=1, number_of_steps=20, orientation="horizontal", command=self.ui_delay_slider_value)
        self.ui_delay_slider.set(0.5)
        self.ui_delay_slider.pack(side="left", padx=2, expand=True, fill="x")

    def creat_guard_process(self):
        # 先创建实例
        guard_instance = Xz()
        # 设置参数
        guard_instance.set_parms(STOPSIGNAL=self.cooperation_mission, event=self.event)
        # 启动循环
        guard_instance.loop()

    def Guard_process(self, *args):

        # 启动线程
        if self.cooperation_mission.get():
            print(f"启动协助邀请线程")
            Guard_process = Thread(target=self.creat_guard_process)
            Guard_process.daemon = True
            Guard_process.start()

        else:
            self.event.set()
            print(f"关闭协助邀请线程")

        pass

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
