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
from PIGEON.threadsafelist import ThreadSafeList
from PIGEON.event import MyEvent
from PIGEON.client import Client
from GUI.tab_pretask import *
from GUI.togglebuton import ToggleButton
from GUI.tab_pretask import AtomTask

# from tool.switchui.SwitchUI import SwitchUI
from page.page_switch import nav
from tool.soulchange.soulchange import SoulChange
from task import *
from threading import Thread
from datetime import datetime, timedelta
from time import sleep
from win11toast import toast


class TimeManager:
    def parse_time_expression(self, expression: str | datetime):
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
            # print(f'{expression} is {time_info.strftime("%Y-%m-%d %H:%M:%S")}')
            # 如果当前时间晚于 "after" 的时间，返回 True，否则返回 False
            return current_time >= time_info

        # 如果是时间区间的情况
        if isinstance(time_info, tuple) and len(time_info) == 2:
            start_time, end_time = time_info
            # print(f"start_time: {start_time}, end_time: {end_time},current_time: {current_time}")
            return start_time <= current_time <= end_time

        return False


class TaskManager:
    def __init__(self):
        self.ready_tasks = ThreadSafeList()
        self.wait_tasks = ThreadSafeList()

    def delete_task(self, task: AtomTask):
        """在队列内寻找对应的任务并删除"""
        if task in self.ready_tasks:
            self.ready_tasks.remove(task)
            log.debug(f"delete {task.name} task from ready_tasks.")
            task.destroy()
        elif task in self.wait_tasks:
            self.wait_tasks.remove(task)
            log.debug(f"delete {task.name} task from wait_tasks.")
            task.destroy()
        else:
            print("任务不存在")

    def is_ready_to_run(self):
        """
        判断是否有实时任务可以立即执行。
        """
        for task in self.wait_tasks:
            # log.insert("5.1", f"wait_tasks={[task.name for task in self.wait_tasks]}")
            try:
                task.task_name.configure(fg_color="#4a86e8")
                if task.parms.get("next_time"):
                    if self.is_time_valid(task.parms.get("next_time")):
                        self.ready_tasks.append(task)
                        task.set_state("ready")
                        self.wait_tasks.remove(task)
                        print(f"{task.name} is ready to run.next_time: {task.parms.get('next_time')}")
                        continue
                elif self.is_time_valid(task.parms.get("run_time")):
                    if not self.task_ctrl.is_set():
                        log.info_nof(f"{task.name} is ready at {task.parms.get('run_time')}.")
                    self.ready_tasks.append(task)
                    task.set_state("ready")
                    self.wait_tasks.remove(task)
                    continue

            except Exception as e:
                print(f"Error in {task.name} task: {e}")
                continue
            finally:
                try:
                    sleep(0.5)
                    task.task_name.configure(fg_color="skyblue")
                except:
                    pass

    def classify(self, task: AtomTask):
        """
        将任务分类到等待队列或就绪队列。
        """
        # 获取任务的参数
        task.parms = task_option.get(task.name, {})
        # 设置一个获取关机时间的钩子
        now = datetime.now()
        if task.name == "自动关机":
            # 获取当前所有任务列表的最晚执行时间，然后将关机任务的执行时间设置为最晚执行时间的后1分钟
            for _task in self.wait_tasks + self.ready_tasks:
                if _task.name == "自动关机":
                    continue
                if _task.parms.get("next_time"):
                    run_time = self.parse_time_expression(_task.parms.get("next_time"))
                elif _task.parms.get("run_time"):
                    run_time = self.parse_time_expression(_task.parms.get("run_time"))
                else:
                    log.error(f"task {_task.name} has no run_time or next_time parameter.")
                if isinstance(run_time, datetime):
                    if run_time > now:
                        now = run_time
                elif isinstance(run_time, tuple):
                    if run_time[1] > now:
                        now = run_time[1]
            task.parms["run_time"] = f"after {(now + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")}"

        # 优先判断 next_time 参数
        if next_time := task.parms.get("next_time"):  # 如果存在 next_time 参数
            if self.is_time_valid(next_time):
                # print(f"{task.name} is ready to run.next_time: {next_time}")
                self.ready_tasks.append(task)
                task.set_state("ready")
                log.debug(f"{task.name} is add to ready_tasks")
                return  # 任务已分类，不需要重复判断
            else:
                # print(f"{task.name} is not ready to run.next_time: {next_time}")
                self.wait_tasks.append(task)
                task.set_state("waiting")
                log.debug(f"{task.name} is add to wait_tasks")
                return  # 任务已分类，不需要重复判断

        # 检查 run_time 参数
        run_time = task.parms.get("run_time")
        if run_time is not None:  # 如果存在 run_time 参数
            if self.is_time_valid(run_time):
                self.ready_tasks.append(task)
                task.set_state("ready")
                log.debug(f"{task.name} is add to ready_tasks")
            else:
                self.wait_tasks.append(task)
                task.set_state("waiting")
                log.debug(f"{task.name} is add to wait_tasks")
        else:
            # 如果没有 run_time，直接归入等待队列
            self.wait_tasks.append(task)
            task.set_state("waiting")
            log.debug(f"{task.name} is add to wait_tasks")

    def get_state(self, task_id):

        if self.is_time_valid(task_option[task_id]["run_time"]):
            print(f"{task_id} is ready to run.task_parms: {task_option[task_id]}")
            return "ready"
        else:
            return "waiting"


class TaskExecutor:

    def __init__(self):
        self.task_ctrl = MyEvent("task_ctrl")
        self.is_task_running = False
        self.switch_ui = nav  # SwitchUI(running=self.task_ctrl)
        self.soul_change = SoulChange(running=self.task_ctrl)
        pass

    def _rt_task_loop(self, task: ToggleButton = None, parms: dict = None):
        log.clear()
        log.insert("1.0", f"{'━'*14}统计{'━'*14}\n\n\n\n\n{'━'*14}日志{'━'*14}\n", tags="sep")
        log.info(f"ui_delay : {parms.get('ui_delay'):.3f} seconds")
        # 创建task任务实例
        task_cls = Task[task.name].value
        assert task_cls is not None, f"未找到任务类 {task.name}"
        task_instance = task_cls(STOPSIGNAL=self.task_ctrl)
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
            toast(f"{task.name} 任务已结束")
        pass

    def _sche_task_loop(self, task: AtomTask = None, parms: dict = None):
        self.is_task_running = True
        log.clear()
        log.insert("1.0", f"{'━'*14}统计{'━'*14}\n\n\n\n\n{'━'*14}日志{'━'*14}\n", tags="sep")
        try:
            self._task_need_change_soul(parms)
            self._task_need_switch_page(parms, "start_ui")
            if not self.task_ctrl.is_set():
                log.info(f"Stoped {task.name} task.")
                return
            instance_return = self._create_task_instance(parms)
            self._task_need_switch_page(parms, "end_ui")
            log.file(f"instance_return: {instance_return}")
        except Exception as e:
            log.info(f"_task function Error in {parms['task_id']} task: {e}")

        finally:
            try:
                if instance_return:
                    # 如果任务有下一次运行时间，则更新任务的 next_time 参数
                    pattern = r"^[0-2][0-9]:[0-5][0-9]:[0-5][0-9]$"
                    if bool(re.match(pattern, instance_return)):
                        hour, minute, second = map(int, instance_return.split(":"))
                        target_time = datetime.now() + timedelta(hours=hour, minutes=minute, seconds=second)
                        task_option[task.name]["next_time"] = f"after {target_time.strftime("%Y-%m-%d %H:%M:%S")}"
                        task.TabMaster.add_task(task.name)
            except:
                pass
            task.set_state("done")
            task.TabMaster.sort_task()
            self.task_ctrl.stop()
            self.is_task_running = False

        pass

    def execute(self, task: AtomTask | ToggleButton):
        try:
            # 实时任务立即执行
            if isinstance(task, ToggleButton):
                task_is_off = not task.is_on
                is_stopped = self.task_ctrl.state == "STOP"
                is_running = self.task_ctrl.state == "RUNNING"

                if task_is_off and is_stopped:  # 任务未开启，且当前状态为停止
                    parms = {k: v.get() for k, v in task.values.items() if v is not None}
                    # print(f'即时任务参数：{[f"{k}:{v}" for k,v in parms.items()]}')
                    thread = Thread(target=self._rt_task_loop, kwargs={"task": task, "parms": parms})
                    thread.daemon = True
                    thread.start()
                    self.task_ctrl.start()
                elif is_running and task_is_off:
                    log.info("已有任务在运行，请先停止当前任务")
                    task.toggle_change()
                elif task.is_on and is_running:
                    self.task_ctrl.stop()

            elif isinstance(task, AtomTask) and self.task_ctrl.state == "STOP":
                self.task_ctrl.start()
                thread = Thread(target=self._sche_task_loop, kwargs={"task": task, "parms": task.parms})
                thread.daemon = True
                thread.start()

        except Exception as e:
            log.error(f"执行任务时发生错误: {e}")
            self.task_ctrl.stop()
            if isinstance(task, ToggleButton):
                task.toggle_change()
            elif isinstance(task, AtomTask):
                task.set_state("error")

    def _create_task_instance(self, parms):
        try:
            log.info(f"Start {parms['task_id']} task.")
            task_cls = Task[parms["task_id"]].value
            assert task_cls is not None, f"未找到任务类 {parms['task_id']}"
            task_instance = task_cls(STOPSIGNAL=self.task_ctrl)
            task_instance.set_parms(**parms)
            task_instance.loop()
            return getattr(task_instance, "next_time", None)
        except Exception as e:
            log.info(f"Error in {parms['task_id']} task: {e}")
            return None
        finally:
            del task_instance
            log.info(f"{parms['task_id']} task instance finnally exit.")

    def _task_need_change_soul(self, parms):
        if parms.get("change_soul", "false") != "false":
            self.soul_change.changeSoulTo(parms["change_soul"], self.task_ctrl)

    def _task_need_switch_page(self, parms, page):
        if parms.get(page, False) and self.task_ctrl.is_set():
            self.switch_ui.switch_to(parms[page], self.task_ctrl)


class ClientManager:
    def __init__(self):
        self.client_ctrl = MyEvent("client_ctrl")
        self.client = Client(self.client_ctrl)

    def _is_client_started(self):
        """
        启动客户端
        """
        if not self.client.is_app_started():
            print("客户端未启动，正在启动客户端")
            self.client_ctrl.start()  # 启动客户端线程
            self.client.client_start()  # 启动客户端
            # 等待客户端启动完成，避免任务执行时客户端还未启动完成
            print("等待客户端启动完成")
            while 1:
                if self.client.verify_app_start_finish():
                    break
                if self.client.imgrec.win.is_windows_exist():  # self.client.imgrec.win.is_window_top() and
                    self.client.imgrec.win.set_window_bottom()
                    sleep(0.05)
        else:
            print("客户端已启动，开始执行任务")
            return  # 客户端已启动，不需要再启动客户端


class GUIInterface:
    def submit_task(self, task: AtomTask | ToggleButton):
        """
        提交任务到队列。或者直接执行
        """
        if isinstance(task, ToggleButton):
            self.execute(task)
        elif isinstance(task, AtomTask):
            self.classify(task)


class Scheduler(TimeManager, TaskManager, TaskExecutor, ClientManager, GUIInterface):

    tab_frame = None

    def __init__(self):
        TimeManager.__init__(self)
        TaskManager.__init__(self)
        TaskExecutor.__init__(self)
        ClientManager.__init__(self)
        GUIInterface.__init__(self)

        self.scheduler_ctrl = MyEvent("scheduler_ctrl")

    def scheduler_loop(self):
        """
        检查等待任务队列是否有任务符合执行的时间条件
        如果有，则将该任务从等待队列移动到就绪队列。
        从就绪队列中取出任务，执行任务。
        实时任务立即执行。
        """
        while self.scheduler_ctrl.is_set():
            sleep(1)
            # self.tab_frame.state_loop()
            # 检查等待任务队列是否有任务符合执行的时间条件
            self.is_ready_to_run()
            # 从就绪队列中取出任务，执行任务
            if self.task_ctrl.state == "STOP" and self.ready_tasks:

                if self.is_task_running:
                    log.warning("已有任务正在执行：{}")
                    continue
                else:
                    # 取出任务并执行
                    current_task = self.ready_tasks.pop(0)
                    log.info(f"pop out {current_task.name} task.")
                    current_task.set_state("running")
                    # 执行任务之前检查客户端是否启动
                    self._is_client_started()
                    self.execute(current_task)

            elif self.task_ctrl.state == "STOP" and not self.ready_tasks:  # 无任务运行，同时ready_tasks为空,此时关闭客户端
                self.client.client_stop()  # 关闭客户端
                pass

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
        """
        停止调度器
        """
        return self.scheduler_ctrl.clear()


scheduler = Scheduler()
