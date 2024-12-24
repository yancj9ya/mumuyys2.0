import customtkinter as ctk
import json
import tkinter.messagebox as messagebox
from PIGEON.config import task_option
from PIGEON.log import log
from GUI.icons.icons import Icons
from PIL import Image, ImageTk

# from PIGEON.scheduler import scheduler


class SetOption(ctk.CTkFrame):
    def __init__(self, master, name, value, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.grid_rowconfigure(0, minsize=30)
        self.grid_columnconfigure(0, minsize=100)
        self.grid_columnconfigure(1, minsize=200)
        self.name = name
        self.value = value
        self.set_option_name = ctk.CTkLabel(self, text=name, font=("微软雅黑", 12, "bold"))
        self.set_option_value = ctk.CTkEntry(self, width=10, corner_radius=8)
        self.set_option_value.insert(0, value)
        self.set_option_name.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        self.set_option_value.grid(row=0, column=1, padx=2, pady=2, sticky="ew")


class TaskSettingWindow(ctk.CTkToplevel):
    def __init__(self, task, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = task.winfo_toplevel()
        self.geometry("330x330+{}+{}".format(self.main_window.winfo_x() - 440, self.main_window.winfo_y()))
        self.task = task
        self.title(f"{task.task_name.cget('text')}任务设置")
        self.resizable(False, False)

        self.create_option()
        self.complete_btn = ctk.CTkButton(self, text="完成", command=self.complete_set, width=20, corner_radius=8)
        self.complete_btn.pack(pady=2)

    def create_option(self):
        try:
            task_name = self.task.task_name.cget("text")
            for option, value in task_option.get(task_name, {}).items():
                option_s = SetOption(self, option, value)
                option_s.pack(pady=2)
        except FileNotFoundError:
            messagebox.showerror("错误", "文件未找到，请检查文件路径。")
        except json.JSONDecodeError:
            messagebox.showerror("错误", "文件内容不是有效的 JSON 格式。")
        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {e}")

    def complete_set(self):
        task_name = self.task.task_name.cget("text")
        # 更新 JSON 数据
        try:

            for set in self.winfo_children():
                if isinstance(set, SetOption):
                    print(set.name, set.set_option_value.get())
                    task_option.get(task_name)[set.name] = set.set_option_value.get()

        except FileNotFoundError:
            messagebox.showerror("错误", "文件未找到，请检查文件路径。")
        except json.JSONDecodeError:
            messagebox.showerror("错误", "文件内容不是有效的 JSON 格式。")
        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {e}")

        self.destroy()  # 关闭窗口


class AtomTask(ctk.CTkFrame):
    scheduler = None

    def __init__(self, master, task_name, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.toplevel_window = None
        self.name = task_name
        self.parms = task_option.get(task_name, {})

        self.grid_columnconfigure(0, minsize=90)
        self.grid_columnconfigure(1, minsize=80)
        self.grid_columnconfigure([2, 3], minsize=40)
        self.task_name = ctk.CTkLabel(self, text=task_name, width=50, fg_color="skyblue", font=("微软雅黑", 11, "bold"), corner_radius=8)
        self.task_name.grid(row=0, column=0, padx=1, pady=2, sticky="ew")
        self.task_state = ctk.CTkLabel(self, text="running", fg_color="green", corner_radius=8)
        self.task_state.grid(row=0, column=1, padx=1, pady=2, sticky="ew")
        self.setting_btn = ctk.CTkButton(self, text="设置", command=self.set_task, width=8, corner_radius=8)
        self.setting_btn.grid(row=0, column=2, padx=1, pady=2, sticky="e")
        self.del_btn = ctk.CTkButton(self, text="删除", command=self.del_task, width=8, corner_radius=8)
        self.del_btn.grid(row=0, column=3, padx=1, pady=2, sticky="w")

        self.state = self.scheduler.get_state(task_name)
        self.set_state(self.state)

    def set_task(self):
        if self.setting_btn.cget("text") == "设置":
            if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
                self.toplevel_window = TaskSettingWindow(self)
            else:
                self.toplevel_window.focus()
        elif self.setting_btn.cget("text") == "取消":
            self.scheduler.task_ctrl.stop()

    @property
    def TabMaster(self):
        return self.master.master.master.master

    def del_task(self):
        try:
            if self.del_btn.cget("text") == "删除":
                if self.task_state.cget("text") == "running":
                    messagebox.showwarning("警告", "任务正在运行，无法删除。")
                elif self.task_state.cget("text") in ["waiting", "ready"]:
                    result = messagebox.askyesno("确认删除", "您确定要删除这个任务吗？")
                    if result:
                        self.scheduler.delete_task(self)
                        self.destroy()  # 摧毁控件
                else:
                    self.destroy()  # 摧毁控件
            elif self.del_btn.cget("text") == "暂停":
                if self.scheduler.task_ctrl.state == "RUNNING":
                    self.scheduler.task_ctrl.wait()
                    self.del_btn.configure(text="恢复")
            elif self.del_btn.cget("text") == "恢复":
                if self.scheduler.task_ctrl.state == "WAIT":
                    self.scheduler.task_ctrl.start()
                    self.del_btn.configure(text="暂停")
        except Exception as e:
            messagebox.showerror("错误", f"操作失败: {e}")

    def set_state(self, state):
        try:
            if state == "running":
                self.task_state.configure(text=state, fg_color="Goldenrod")
                self.del_btn.configure(text="暂停")
                self.setting_btn.configure(text="取消", fg_color="red")
            elif state == "ready":
                self.task_state.configure(text=state, fg_color="lightgreen")
            elif state == "waiting":
                self.task_state.configure(text=state, fg_color="lightyellow")
            elif state == "done":
                self.task_state.configure(text=state, fg_color="lightgray")
                self.del_btn.configure(text="删除")
                self.setting_btn.configure(text="设置", fg_color="skyblue")
        except Exception as e:
            log.error(f"设置任务状态失败: {e}")


class PreTaskTab(ctk.CTkFrame):
    trans_task = None
    start_manager = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_rowconfigure(1, minsize=340)
        self.grid_columnconfigure(0, minsize=80)
        self.task_start = ctk.CTkButton(self, text="开始运行", fg_color="green", command=self.scheduler_switch, width=30, corner_radius=2)
        self.task_start.grid(row=0, column=1, padx=2, pady=2, sticky="w")
        self.scheduler_state = ctk.CTkLabel(self, text="🐱", fg_color="transparent", width=30, text_color="green", font=("微软雅黑", 18, "bold"))
        self.scheduler_state.grid(row=0, column=2, padx=2, pady=2, sticky="w")

        try:
            self.task_frame_ = task_option.json
            self.add_task_btn = ctk.CTkOptionMenu(self, values=list(self.task_frame_.keys()), command=self.add_task, width=80, corner_radius=2, anchor="center")
            self.add_task_btn.grid(row=0, column=0, padx=2, pady=2, sticky="ew")

            self.task_frame = ctk.CTkScrollableFrame(self, width=228, height=240, corner_radius=0)
            self.task_frame.grid(row=1, column=0, columnspan=4, padx=1, pady=2, sticky="nsew")
        except FileNotFoundError:
            messagebox.showerror("错误", "任务列表文件未找到，请检查文件路径。")
        except json.JSONDecodeError:
            messagebox.showerror("错误", "任务列表文件内容不是有效的 JSON 格式。")

    def state_loop(self):
        try:
            # print("state_loop")
            current_text = self.scheduler_state.cget("text")
            # 定义状态转换字典
            state_transition = {" 🐱": "🐱", "🐱": " 🐱"}
            # 更新状态
            if current_text in state_transition:
                self.scheduler_state.configure(text=state_transition[current_text])
        except Exception as e:
            messagebox.showerror("错误", f"状态循环操作失败: {e}")

    def add_task(self, task_name):
        new_task = AtomTask(self.task_frame, task_name)
        new_task.scheduler.submit_task(new_task)
        self.sort_task()

    def sort_task(self):
        """
        排序任务列表
        running ->ready -> waiting ->  done
        """
        # 定义任务状态的优先级
        state_priority = {"running": 1, "ready": 2, "waiting": 3, "done": 4}
        task_pool = self.task_frame.winfo_children()
        # 按照状态优先级进行排序
        sorted_tasks = sorted(task_pool, key=lambda task: state_priority[task.task_state.cget("text")])

        # 更新每个任务的布局
        for idx, task in enumerate(sorted_tasks):
            task.grid(row=idx, column=0, padx=2, pady=2, sticky="ew")

    def scheduler_switch(self):
        try:
            if self.task_start.cget("text") == "开始运行":
                AtomTask.scheduler.tab_frame = self
                AtomTask.scheduler.start_scheduler()
                self.task_start.configure(text="停止运行", fg_color="red")
            else:
                AtomTask.scheduler.stop_scheduler()
                self.task_start.configure(text="开始运行", fg_color="green")
        except Exception as e:
            messagebox.showerror("错误", f"操作失败: {e}")
