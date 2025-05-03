import customtkinter as ctk
from GUI.togglebuton import ToggleButton
from threading import Thread
from task import Xz


class SettingTab(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.thread_created = False
        # create viriables
        self.cooperation_mission_var = ctk.BooleanVar(value=True)
        self.cooperation_mission_var.trace_add("write", self.set_cooperation)
        self.keep_level_var = ctk.BooleanVar(value=True)
        self.set_window_top_var = ctk.IntVar(value=1)
        self.set_window_top_var.trace_add("write", self.set_window_top)
        self.ui_delay_var = ctk.DoubleVar(value=0.5)
        # 绑定变量到ToggleButton类
        ToggleButton.values.update({"tp_keep_level": self.keep_level_var, "ui_delay": self.ui_delay_var, "set_window_top": self.set_window_top_var, "cooperation_mission": self.cooperation_mission_var})

        # create layout
        self.group0 = ctk.CTkScrollableFrame(self, label_text="探索设置", height=10)
        self.group0._scrollbar.configure(width=0)
        self.group0.pack(fill="both", pady=2)
        self.line1 = ctk.CTkFrame(self.group0, fg_color="transparent")
        self.line1.pack(fill="x", pady=5)
        self.line2 = ctk.CTkFrame(self.group0, fg_color="transparent")
        self.line2.pack(fill="x", pady=5)
        self.line3 = ctk.CTkFrame(self.group0, fg_color="transparent")
        self.line3.pack(fill="x", pady=5)

        # create widgets
        self.cooperation_mission = ctk.CTkSwitch(self.line2, text="协助邀请", variable=self.cooperation_mission_var, command=self.set_cooperation, onvalue=True, offvalue=False)
        self.cooperation_mission.pack(side="left", padx=2)

        self.keep_level_check = ctk.CTkSwitch(self.line2, text="突破保级", variable=self.keep_level_var, onvalue=True, offvalue=False)
        self.keep_level_check.pack(side="left", padx=2, expand=True)

        self.set_window_top_check = ctk.CTkSwitch(self.line3, text="置顶窗口", variable=self.set_window_top_var, onvalue=1, offvalue=0, command=self.set_window_top)
        self.set_window_top_check.pack(side="left", padx=2)

        self.ui_delay_combox = ctk.CTkComboBox(self.line1, values=["0.2", "0.5", "0.7"], width=80, justify="center", variable=self.ui_delay_var, height=20, command=self.ui_delay_slider_value)
        self.ui_delay_combox.set("0.5")
        self.ui_delay_combox.pack(side="left", padx=2)

        self.ui_delay_slider = ctk.CTkSlider(self.line1, from_=0.1, to=1, number_of_steps=20, orientation="horizontal", width=240, command=self.ui_delay_slider_value)
        self.ui_delay_slider.set(0.5)
        self.ui_delay_slider.pack(side="left", padx=2, expand=True, fill="x")

    def set_cooperation(self, *args):
        cooperation_mission = self.cooperation_mission_var.get()
        if cooperation_mission and not self.thread_created:
            auto_accept_invitation = Thread(target=Xz.cooperation_mission_start, kwargs={"STOPSIGNAL": self.cooperation_mission_var})
            auto_accept_invitation.daemon = True
            auto_accept_invitation.start()
            self.thread_created = True
        else:
            try:
                if auto_accept_invitation.is_alived():
                    print(f"thread is not exited, stop it")
            except NameError:
                self.thread_created = False

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
