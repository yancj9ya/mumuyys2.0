from PIGEON.log import log
from threading import Thread, Event
from task import Xz, Tp, Dg, Ltp, Ql, Hd, Ts, Yh
from win11toast import toast
from time import sleep

# log = Log()


class Task:
    TASK_PROCESS = "STOP"
    STOPSIGNAL = Event()
    F_MAP = {"结界突破": Tp, "道馆": Dg, "寮突破": Ltp, "契灵": Ql, "智能": Hd, "绘卷": Ts, "御魂": Yh}

    @classmethod
    def execute_task(cls, **kwargs):

        # 获取任务名称,参数
        task = kwargs.get("event")
        task_parms = {k: v.get() for k, v in kwargs.get("values").items() if v is not None}
        # 执行停止任务逻辑
        if task.cget("text") == "STOP":
            cls.STOPSIGNAL.clear()
            log.debug(f"Task stop signal received")
            return
        else:
            if cls.TASK_PROCESS == "RUNNING":
                log.error(f"Task already running")
                task.toogle_change()
                return
            log.info(f"Task {task.cget('text')} started")
            cls.STOPSIGNAL.set()

            # 执行任务
            Thread(target=cls.start_task, kwargs={"task": task, "task_parms": task_parms, "STOPSIGNAL": cls.STOPSIGNAL}).start()
            # 创建协助自动接受进程
            Thread(target=Xz.start_deamon, kwargs={"STOPSIGNAL": cls.STOPSIGNAL}).start()

    @classmethod
    def start_task(cls, task=None, task_parms=None, STOPSIGNAL=None, **kwargs):
        log.clear()
        log.insert("1.0", f"{'━'*14}统计{'━'*14}\n\n\n\n\n{'━'*14}日志{'━'*14}\n", tags="sep")
        log.info(f"ui_delay : {task_parms.get('ui_delay'):.3f} seconds")
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
        log.error(f"test error message")
        log.debug(f"test debug message")
        kwargs.get("Task").toggle_change()
        toast(f"{kwargs.get('Task').name}", f"任务已完成")
