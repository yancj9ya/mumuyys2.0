# 一个新的调度器的更严密的实现
# 任务区分为两种：
# 1. 实时任务：实时任务的调度是最高优先级的，必须在规定时间内完成。
# 2. 计划任务：计划任务的调度次之，但也不能完全忽略。
# 对于计划任务，调度器会根据任务的可运行时间，添加到不同的管道中
# 实时任务则会被立即调度。
# 调度器会根据任务的优先级，将实时任务和计划任务分开处理。
# 实时任务的调度是最高优先级的
# 与GUI的接口，调度器会将任务的状态反馈给GUI。
# GUI通过调用调度器的接口，可以向调度器提交任务，并获取任务的状态。删除任务。
import re
from PIGEON.config import task_option
from PIGEON.log import log
from PIGEON.event import MyEvent
from GUI.tab_pretask import *
from GUI.togglebuton import ToggleButton
from task.based.switchui.SwitchUI import SwitchUI
from task.based.soulchange.soulchange import SoulChange
from task import Xz, Tp, Dg, Ltp, Ql, Hd, Ts, Yh, Ad, Jy
from threading import Thread
from datetime import datetime, timedelta
from time import sleep


class Scheduler:
    F_MAP = {"结界寄养": Jy, "结界突破": Tp, "地域鬼王": Ad, "寮突破": Ltp, "契灵": Ql, "智能": Hd, "绘卷": Ts, "御魂": Yh, "道馆": Dg}

    def __init__(self):
        self.task_ctrl = MyEvent("task_ctrl")
        self.scheduler_ctrl = MyEvent("scheduler_ctrl")

        self.ready_tasks = []
        self.wait_tasks = []

        self.switch_ui = SwitchUI(running=self.task_ctrl)
        self.soul_change = SoulChange(running=self.task_ctrl)

    def submit_task(self, task: AtomTask | ToggleButton):
        """
        提交任务到队列。或者直接执行
        """
        if isinstance(task, ToggleButton):
            self.excute(task)
        elif isinstance(task, AtomTask):
            self.classify(task)

    def excute(self, task: AtomTask | ToggleButton):
        # 实时任务立即执行
        if isinstance(task, ToggleButton):
            if not task.is_on and self.task_ctrl.state == "STOP":  # 任务未开启，且当前状态为停止
                parms = {k: v.get() for k, v in task.values.items() if v is not None}
                thread = Thread(target=self._rt_task_loop, kwargs={"task": task, "parms": parms})
                thread.daemon = True
                thread.start()
                self.task_ctrl.start()
            elif self.task_ctrl.state == "RUNNING" and not task.is_on:
                log.info(f"已有任务在运行，请先停止当前任务")
                task.toggle_change()
            elif task.is_on and self.task_ctrl.state == "RUNNING":
                self.task_ctrl.stop()
            pass
        elif isinstance(task, AtomTask):
            if self.task_ctrl.state == "STOP":
                self.task_ctrl.start()
                thread = Thread(target=self._sche_task_loop, kwargs={"task": task, "parms": task.parms})
                thread.daemon = True
                thread.start()
                task.set_state("running")
            pass

    def _sche_task_loop(self, task: AtomTask = None, parms: dict = None):
        log.clear()
        log.insert("1.0", f"{'━'*14}统计{'━'*14}\n\n\n\n\n{'━'*14}日志{'━'*14}\n", tags="sep")
        try:
            self._task_need_change_soul(parms)
            while not self.switch_ui.switch_to(parms["start_ui"]):
                continue
            instance_return = self._create_task_instance(parms)
            print(f"instance_return: {instance_return}")

        except Exception as e:
            log.info(f"_task function Error in {parms['task_id']} task: {e}")

        finally:
            if instance_return:
                # 如果任务有下一次运行时间，则更新任务的 next_time 参数
                pattern = r"^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$"
                if bool(re.match(pattern, instance_return)):
                    hour, minute, second = map(int, instance_return.split(":"))
                    target_time = datetime.now() + timedelta(hours=hour, minutes=minute, seconds=second)
                    task_option[task.name]["next_time"] = target_time.strftime("%Y-%m-%d %H:%M:%S")
                    task.TabMaster.add_task(task.name)

            self.switch_ui.switch_to(parms["end_ui"])
            task.set_state("done")
            task.TabMaster.sort_task()
            self.task_ctrl.stop()

        pass

    def _create_task_instance(self, parms):
        try:
            log.info(f"Start {parms['task_id']} task.")
            task_instance = self.F_MAP.get(parms["task_id"])(STOPSIGNAL=self.task_ctrl)
            task_instance.set_parms(**parms)
            task_instance.loop()
            return getattr(task_instance, "next_time", None)
        except Exception as e:
            log.info(f"Error in {parms['task_id']} task: {e}")
            return None
        finally:
            log.info(f"End {parms['task_id']} task.")

    def _task_need_change_soul(self, parms):
        if parms.get("change_soul") != "false":
            self.soul_change.changeSoulTo(parms["change_soul"])

    def _rt_task_loop(self, task: ToggleButton = None, parms: dict = None):
        log.clear()
        log.insert("1.0", f"{'━'*14}统计{'━'*14}\n\n\n\n\n{'━'*14}日志{'━'*14}\n", tags="sep")
        log.info(f"ui_delay : {parms.get('ui_delay'):.3f} seconds")
        # 创建task任务实例
        task_instance = self.F_MAP.get(task.name)(STOPSIGNAL=self.task_ctrl, parms=parms)
        # 设置参数
        # print(f"parms: {parms}")
        task_instance.set_parms(**parms)
        # 启动任务循环
        task_instance.loop()
        # 等待任务结束
        if task.is_on:
            task.toggle_change()
        if self.task_ctrl.state == "RUNNING":
            self.task_ctrl.stop()
        pass

    def scheduler_loop(self):
        """
        检查等待任务队列是否有任务符合执行的时间条件
        如果有，则将该任务从等待队列移动到就绪队列。
        从就绪队列中取出任务，执行任务。
        实时任务立即执行。
        """
        while self.scheduler_ctrl.is_set():
            # 检查等待任务队列是否有任务符合执行的时间条件
            self.is_ready_to_run()
            # 从就绪队列中取出任务，执行任务
            if self.task_ctrl.state == "STOP" and self.ready_tasks:
                self.excute(self.ready_tasks.pop(0))
            elif self.task_ctrl.state == "RUNNING":
                pass
            sleep(1.5)
        pass

    def start_scheduler(self):
        """
        启动调度器
        """
        self.scheduler_ctrl.start()
        thread = Thread(target=self.scheduler_loop)
        thread.daemon = True
        thread.start()
        pass

    def stop_scheduler(self):
        self.scheduler_ctrl.stop()
        if self.task_ctrl.state == "RUNNING":
            self.task_ctrl.stop()
            print("stop scheduler and task")
        pass

    def delete_task(self, task: AtomTask):
        """在队列内寻找对应的任务并删除"""
        if task in self.ready_tasks:
            self.ready_tasks.remove(task)
        elif task in self.wait_tasks:
            self.wait_tasks.remove(task)
        else:
            print("任务不存在")

    def is_ready_to_run(self):
        """
        判断是否有实时任务可以立即执行。
        """
        for task in self.wait_tasks:
            self.classify(task)
            # if self.is_time_valid(task.parms["run_time"]):
            #     self.ready_tasks.append(task)
            #     self.wait_tasks.remove(task)
            #     task.set_state("ready")

    def classify(self, task: AtomTask):
        """
        将任务分类到等待队列或就绪队列。
        """
        # 获取任务的参数
        task.parms = task_option.get(task.name, {})

        # 优先判断 next_time 参数
        next_time = task.parms.get("next_time")
        if next_time is not None:  # 如果存在 next_time 参数
            if self.is_time_valid(next_time):
                # print(f"{task.name} is ready to run.next_time: {next_time}")
                self.ready_tasks.append(task)
                task.set_state("ready")
                return  # 任务已分类，不需要重复判断
            else:
                # print(f"{task.name} is not ready to run.next_time: {next_time}")
                self.wait_tasks.append(task)
                task.set_state("waiting")
                return  # 任务已分类，不需要重复判断

        # 检查 run_time 参数
        run_time = task.parms.get("run_time")
        if run_time is not None:  # 如果存在 run_time 参数
            if self.is_time_valid(run_time):
                self.ready_tasks.append(task)
                task.set_state("ready")
            else:
                self.wait_tasks.append(task)
                task.set_state("waiting")
        else:
            # 如果没有 run_time，直接归入等待队列
            self.wait_tasks.append(task)
            task.set_state("waiting")

    def get_state(self, task_id):

        if self.is_time_valid(task_option[task_id]["run_time"]):
            print(f"{task_id} is ready to run.task_parms: {task_option[task_id]}")
            return "ready"
        else:
            return "waiting"

    def parse_time_expression(self, expression: str):
        """
        解析时间表达式。
        """
        current_time = datetime.now()

        # 处理 "right now"
        if expression.lower() == "right now":
            return current_time

        # 处理 "after 6:00"
        match = re.match(r"after (\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]) (\d{1,2}):([0-5][0-9]):([0-5][0-9])", expression, re.IGNORECASE)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            hour = int(match.group(4))
            minute = int(match.group(5))
            second = int(match.group(6))

            # 创建提取的时间对象
            return datetime(year, month, day, hour, minute, second)

        # 处理 "21:00-24:00"
        match = re.match(r"(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})", expression, re.IGNORECASE)
        if match:
            start_hour = int(match.group(1))
            start_minute = int(match.group(2))
            end_hour = int(match.group(3))
            end_minute = int(match.group(4))

            start_time = current_time.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            end_time = current_time.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)

            # 如果结束时间小于当前时间，可能是第二天的时间
            if end_time < start_time:
                # end_time += timedelta(days=1)
                if current_time >= end_time:
                    end_time += timedelta(days=1)
                elif current_time < start_time:
                    start_time -= timedelta(days=1)

            return (start_time, end_time)

        # 如果无法识别，返回 None
        return None
        pass

    def is_time_valid(self, expression):
        """
        判断当前时间是否匹配时间表达式。
        """
        current_time = datetime.now()
        time_info = self.parse_time_expression(expression)

        if time_info is None:
            return False

        # 如果是 "right now" 的情况，直接判断
        if expression.lower() == "right now":
            return current_time == time_info

        # 如果是 "every day after" 的情况
        if isinstance(time_info, datetime):
            # 如果当前时间晚于 "after" 的时间，返回 True，否则返回 False
            return current_time >= time_info

        # 如果是时间区间的情况
        if isinstance(time_info, tuple) and len(time_info) == 2:
            start_time, end_time = time_info
            # print(f"start_time: {start_time}, end_time: {end_time},current_time: {current_time}")
            return start_time <= current_time <= end_time

        return False


scheduler = Scheduler()
