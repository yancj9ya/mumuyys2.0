from PIGEON.log import Log
from threading import Thread, Event
from task import Tp, Dg, Ltp, Ql, Hd, Ts, Yh

from time import sleep

log = Log()


class Task:
    TASK_PROCESS = "STOP"
    STOPSIGNAL = Event()
    F_MAP = {"tp_btn": Tp, "dg_btn": Dg, "ltp_btn": Ltp, "ql_btn": Ql, "hd_btn": Hd, "ts_btn": Ts, "yh_btn": Yh}

    @classmethod
    def execute_task(cls, **kwargs):

        # 获取任务名称,参数
        task = kwargs.get("event")
        task_parms = {k: v.get() for k, v in kwargs.get("values").items() if v is not None}
        # 执行停止任务逻辑
        if task.cget("text") == "STOP":
            cls.STOPSIGNAL.clear()
            log.info(f"Task stop signal received")
            return
        else:
            log.info(f"Task {task.cget('text')} started")
            cls.STOPSIGNAL.set()
            if cls.TASK_PROCESS == "RUNNING":
                log.info(f"Task already running")
                return
            # 执行任务
            Thread(target=cls.start_task, kwargs={"task": task, "task_parms": task_parms, "STOPSIGNAL": cls.STOPSIGNAL}).start()

    @classmethod
    def start_task(cls, task=None, task_parms=None, STOPSIGNAL=None, **kwargs):
        # 创建task任务实例
        task_instance = cls.F_MAP.get(task.name)(STOPSIGNAL=STOPSIGNAL, **kwargs)
        # 设置参数
        print(f"Setting task parameters {task_parms}")
        task_instance.set_parms(**task_parms)
        # 启动任务线程
        cls.TASK_PROCESS = "RUNNING"
        task_instance.loop()
        # 等待任务结束
        cls.TASK_PROCESS = "STOP"
        if STOPSIGNAL.is_set():
            cls.task_finished(Task=task)
            STOPSIGNAL.clear()

    @classmethod
    def task_finished(cls, **kwargs):
        log.info(f"Task {kwargs.get('Task').name} toggled")
        kwargs.get("Task").toggle_change()
