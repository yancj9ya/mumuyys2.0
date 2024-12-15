# this file is used to manage the tasks in the PIGEON system.
from time import sleep
from threading import Thread, Event
from datetime import datetime, timedelta
import json
from task import Xz, Tp, Dg, Ltp, Ql, Hd, Ts, Yh, Ad, Jy
from task.based.switchui.SwitchUI import SwitchUI
from task.based.soulchange.soulchange import SoulChange
from PIGEON.log import log
from PIGEON.MidTrans import Task
from PIGEON.config import task_option


class TaskManager:
    F_MAP = {"结界寄养": Jy, "结界突破": Tp, "地域鬼王": Ad, "寮突破": Ltp, "契灵": Ql, "智能": Hd, "绘卷": Ts, "御魂": Yh, "道馆": Dg}
    STOPSIGNAL = Event()
    scheduler_event = Event()

    def __init__(self):
        self.tasks_ready = []
        self.tasks_waiting = []
        self.tasks_completed = []
        self.running_task = None
        self.running_state = False
        self.switch_ui = SwitchUI(running=self.STOPSIGNAL)
        self.soul_change = SoulChange(running=self.STOPSIGNAL)

    def Gui_to_manager(self, **kwargs):
        action = kwargs["action"]
        task = kwargs.get("add_task") or kwargs.get("del_task")

        if action == "add":
            self.decide_pool(task)
        elif action == "remove":
            self.remove_task(task)

    def remove_task(self, task):
        if self.running_task == task:
            self.running_task = None
        else:
            if task in self.tasks_ready:
                self.tasks_ready.remove(task)
            elif task in self.tasks_waiting:
                self.tasks_waiting.remove(task)

    def decide_pool(self, task):
        try:
            task_config = task_option.get(task.name, {})
            run_time = task_config.get("run_time", "").split("-")

            if len(run_time) != 2:
                log.warning(f"{task.name} task has invalid run_time configuration.")
                return

            start_time, end_time = map(lambda t: datetime.strptime(t, "%H:%M").time(), run_time)
            current_time = datetime.now().time()

            is_current_time_valid = (start_time <= current_time <= end_time) if end_time >= start_time else (current_time < end_time or current_time > start_time)

            if is_current_time_valid:
                if task not in self.tasks_ready:
                    (self.tasks_ready.insert(0, task) if task.name == "结界寄养" else self.tasks_ready.append(task))
                    task.set_state("ready")
                    log.info(f"{task.name} is ready to run.")
            else:
                if task not in self.tasks_waiting:
                    self.tasks_waiting.append(task)
                    task.set_state("waiting")
                    task.task_state.configure(fg_color="lightyellow")
                    log.info(f"{task.name} is waiting for start.")

        except Exception as e:
            log.error(f"Error processing task {task.name}: {e}")

    def choose_task(self):
        if self.tasks_ready:
            self.running_task = self.tasks_ready.pop(0)

    def loop_ask(self, **kw):
        log.insert("1.0", f"{'━'*14}统计{'━'*14}\n\n\n\n\n{'━'*14}日志{'━'*14}\n", tags="sep")

        while kw["STOPSIGNAL"].is_set():
            try:
                if not self.running_task and not self.running_state:
                    self.choose_task()
                    for task in self.tasks_waiting:
                        self.decide_pool(task)
                elif not self.running_state and Task.TASK_PROCESS == "STOP":
                    Thread(target=self._task, kwargs={"parms": task_option.get(self.running_task.name, {})}).start()
                    self.running_task.set_state("running")
                    self.running_state = True
                    self.STOPSIGNAL.set()
            except Exception as e:
                log.error(f"Error in loop_ask: {e}")

            sleep(0.5)

    def _task_done(self):
        self.running_task.set_state("done")
        self.running_task.task_state.configure(fg_color="lightgray")
        self.tasks_completed.append(self.running_task)
        self.running_task = None
        self.running_state = False

    def _task_need_change_soul(self, parms):
        if parms.get("change_soul") != "false":
            self.soul_change.changeSoulTo(parms["change_soul"])

    def _create_task_instance(self, parms):
        log.info(f"Start {parms['task_id']} task.")
        task_instance = self.F_MAP.get(parms["task_id"])(STOPSIGNAL=self.STOPSIGNAL)
        task_instance.set_parms(**parms)
        task_instance.loop()
        return getattr(task_instance, "next_time", None)

    def _task(self, parms):
        log.info(f"parms: {parms}")
        try:
            self._task_need_change_soul(parms)
            while not self.switch_ui.switch_to(parms["start_ui"]):
                continue
            instance_return = self._create_task_instance(parms)

            if parms.get("repeat", False):
                print("repeat")
                time_delta = self.calculate_time_delta(instance_return)
                task_config = task_option.get(self.running_task.name, {})
                self.update_task_config(task_config, time_delta)
                self.running_task.task_master().add_task(self.running_task.name)

        except Exception as e:
            log.info(f"_task function Error in {parms['task_id']} task: {e}")

        finally:
            self._task_done()
            while not self.switch_ui.switch_to("home_page_unfold"):
                continue

    def calculate_time_delta(self, instance_return):
        hours, minutes, seconds = map(int, instance_return.split(":"))
        return timedelta(hours=hours, minutes=minutes + 1)

    def update_task_config(self, task_config, time_delta):
        if "run_time" in task_config:
            task_config["run_time"] = (datetime.now() + time_delta).strftime("%H:%M") + "-" + (datetime.now() + time_delta + timedelta(hours=6)).strftime("%H:%M")

    def start_work(self, **kwargs):
        action = kwargs["action"]
        if action == "start":
            self.scheduler_event.set()
            self.STOPSIGNAL.set()
            Thread(target=self.loop_ask, kwargs={"STOPSIGNAL": self.scheduler_event}).start()
            Thread(target=Xz.start_deamon, kwargs={"STOPSIGNAL": self.scheduler_event}).start()
            if kwargs.get("start_btn"):
                kwargs["start_btn"].configure(fg_color="Red", text="正在运行")
        elif action == "stop":
            self.scheduler_event.clear()
            self.STOPSIGNAL.clear()
            self.running_state = False
            if kwargs.get("start_btn"):
                kwargs["start_btn"].configure(fg_color="Green", text="开始运行")


taskManager = TaskManager()
