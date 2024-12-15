import customtkinter as ctk

# from PIGEON.scheduler import scheduler


class ToggleButton(ctk.CTkButton):
    toggle_command = None
    values = {}

    def __init__(
        self,
        master,
        text_on="STOP",
        text_off="OFF",
        color_on="red",
        color_off="green",
        name=None,
        **kwargs,
    ):
        """
        初始化 ToggleButton
        :param master: 父组件
        :param text_on: 按钮在 "ON" 状态时显示的文字
        :param text_off: 按钮在 "OFF" 状态时显示的文字
        :param color_on: 按钮在 "ON" 状态时的背景颜色
        :param color_off: 按钮在 "OFF" 状态时的背景颜色
        :param command: 状态切换时的回调函数（可选）
        """
        self.master = master
        self.name = name
        self.text_on = text_on
        self.text_off = text_off
        self.color_on = color_on
        self.color_off = color_off
        self.commands = self.toggle_command
        self.is_on = False  # 初始状态为 OFF

        # 创建按钮并设置初始样式
        super().__init__(
            master,
            text=self.text_off,
            fg_color=self.color_off,
            command=self.toggle,
            width=68,
            height=20,
            corner_radius=1,
            border_width=1,
            border_color="#d5d283",
            **kwargs,
        )

    def toggle(self):
        """
        切换按钮状态并更新样式
        """

        # 如果提供了回调函数，则在切换时调用
        # print(f"toggle button {self.name} to {self.is_on} and {self.commands}")
        if self.commands:
            self.commands(self)
        self.toggle_change()
        # 更新按钮的文字和背景颜色

    def toggle_change(self):
        self.is_on = not self.is_on

        self.configure(
            text=self.text_on if self.is_on else self.text_off,
            fg_color=self.color_on if self.is_on else self.color_off,
        )


### **测试代码：创建多个 ToggleButton**


def on_toggle(**kwargs):
    print(f"state: {kwargs}")


if __name__ == "__main__":
    # 初始化 customtkinter 应用
    app = ctk.CTk()
    app.title("CTk Toggle Button Example")
    app.geometry("400x300")
    app.resizable(False, False)
    # 创建多个 ToggleButton 实例
    ToggleButton.toggle_command = on_toggle
    button1 = ToggleButton(app, name="button1")
    button1.grid(row=0, column=0, padx=10, pady=10)

    app.mainloop()
