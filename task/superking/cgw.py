# 超鬼王CGW任务代码
from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec
from task.superking.res.img_info_auto_create import *
from tool.based.base.res.base_img import FIGHTING
from time import sleep
from PIGEON.log import log
from tool.Mytool.Counter import Counter


class Cgw:
    def __init__(self, **kwargs):
        self.click = Click()
        self.image_rec = ImageRec()
        self.running = kwargs.get("STOPSIGNAL", True)
        self.times = 0
        self.task_switch = True
        self.counter = Counter("cgw")
        self.ui_delay = 0.5
        self.ui_list = [FIGHTING, CALL_KING, CHALLENGE, READY, VICTORY, JSZ]

    def loop(self):
        """main loop of the program"""
        log.insert("5.0", f"@超鬼王开始 ")
        while self.task_switch:
            match self.running.state:
                case "RUNNING":
                    self.run()
                case "STOP":
                    self.task_switch = False
                    log.insert("2.3", f"@任务已停止 ")
                    return
                case "WAIT":
                    sleep(1)
                    continue
                case _:
                    pass
        pass

    def set_parms(self, *args, **kwargs):
        """设置参数"""
        self.times = int(kwargs.get("times", 0))
        pass

    def run(self):
        """main logics of the program"""
        sleep(self.ui_delay)
        match_result = self.image_rec.match_ui(self.ui_list)
        log.insert("2.1", f"Matched UI: {match_result}")
        match match_result:  # [FIGHTING, CALL_KING, CHALLENGE, READY, VICTORY, JSZ]
            case "CALL_KING":
                log.insert("4.0", f"@召唤鬼王")
                self.click.area_click(CALL_KING[1])
            case "CHALLENGE":
                self.click.area_click(CHALLENGE[1])
            case "READY":
                self.click.area_click(READY[1])
            case "VICTORY":
                self.click.area_click(VICTORY[1])
                self.counter.increment()
                log.insert("3.0", f"@第{self.counter.count}/{self.times}次挑战完成 ")
                if self.counter.compare(self.times):
                    self.task_switch = False
                    log.insert("2.3", f"@任务已完成 ")
                    return
            case "JSZ":
                log.insert("4.0", f"@结算中...")
                sleep(1)
            case "FIGHTING":
                log.insert("4.0", f"@战斗中...")
                sleep(1)
            case _:
                pass
        pass
