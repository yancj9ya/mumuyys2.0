import customtkinter as ctk
from GUI.togglebuton import ToggleButton


class TsTab(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        # Create variables
        self.tp_ticket_limit = ctk.IntVar(value=25)
        self.monster_limit = ctk.IntVar(value=200)
        self.with_tp = ctk.BooleanVar(value=True)
        # 绑定变量到ToggleButton类
        ToggleButton.values.update({"tp_ticket_limit": self.tp_ticket_limit, "monster_limit": self.monster_limit, "with_tp": self.with_tp})

        # layout
        self.group0 = ctk.CTkScrollableFrame(self, label_text="探索设置", height=10)
        self.group0._scrollbar.configure(height=70, width=0)
        self.group0.pack(fill="x", pady=2)
        self.line1 = ctk.CTkFrame(self.group0, fg_color="transparent")
        self.line1.pack(fill="x", padx=10, pady=2)
        self.line2 = ctk.CTkFrame(self.group0, fg_color="transparent")
        self.line2.pack(fill="x", padx=10, pady=2)

        self.group1 = ctk.CTkFrame(self, height=40)
        self.group1.pack(side="top", fill="x")
        self.line3 = ctk.CTkFrame(self.group1, fg_color="transparent")
        self.line3.pack(side="top", fill="x", expand=True)

        # Create widgets
        # 突破上限
        self.tp_ticket_limit_label = ctk.CTkLabel(self.line1, text="  探索突破卷上限  ", font=("微软雅黑", 14))
        self.tp_ticket_limit_label.pack(side="left", padx=10)
        self.tp_ticket_limit_entry = ctk.CTkEntry(self.line1, textvariable=self.tp_ticket_limit, justify="center")
        self.tp_ticket_limit_entry.pack(side="left", expand=True, fill="x")

        # 怪物上限
        self.monster_limit_label = ctk.CTkLabel(self.line2, text="探索进攻怪物上限", font=("微软雅黑", 14))
        self.monster_limit_label.pack(side="left", padx=10)
        self.monster_limit_entry = ctk.CTkEntry(self.line2, textvariable=self.monster_limit, justify="center")
        self.monster_limit_entry.pack(side="left", expand=True, fill="x")

        # 开启突破开关
        self.with_tp_switch = ctk.CTkSwitch(self.line3, text="开启循环突破", variable=self.with_tp, font=("微软雅黑", 14))
        self.with_tp_switch.pack(side="left", padx=5)
        # 开始探索按钮
        self.start_ts_button = ToggleButton(self.line3, text_off="开始探索", name="绘卷", font=("微软雅黑", 14))
        self.start_ts_button.pack(side="right", padx=10, pady=20)
