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
        # Create widgets
        self.tp_ticket_limit_label = ctk.CTkLabel(self, text="TP Ticket Limit:")
        self.tp_ticket_limit_entry = ctk.CTkEntry(self, textvariable=self.tp_ticket_limit, width=50)
        self.monster_limit_label = ctk.CTkLabel(self, text="Monster Limit:")
        self.monster_limit_entry = ctk.CTkEntry(self, textvariable=self.monster_limit, width=50)
        self.with_tp_switch = ctk.CTkSwitch(self, text="开启突破", variable=self.with_tp)
        self.start_ts_button = ToggleButton(self, text_off="开始探索", name="ts_btn")
        # Add widgets to layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.tp_ticket_limit_label.grid(row=0, column=0, padx=0, pady=5, sticky="ew")
        self.tp_ticket_limit_entry.grid(row=0, column=1, padx=0, pady=5, sticky="e")
        self.monster_limit_label.grid(row=1, column=0, padx=0, pady=5, sticky="ew")
        self.monster_limit_entry.grid(row=1, column=1, padx=0, pady=5, sticky="e")
        self.with_tp_switch.grid(row=0, column=2, columnspan=2, padx=0, pady=5, sticky="ew")
        self.start_ts_button.grid(row=1, column=2, padx=10, pady=5, sticky="ew")
