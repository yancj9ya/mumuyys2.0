# 狩猎战


from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec
from tool.based.base.res.base_img import *
from task.hunt.res.img_info_auto_create import *
from time import sleep
from PIGEON.log import log
import datetime


class Hunt:

    def __init__(self, **kwargs):
        self.Click = Click()
        self.ImgRec = ImageRec()
        self.uilist = [FIGHTING, HUNT_END, HUNT_VICTORY, MAIN_ENTRANCE, SECOND_ENTRANCE, HUNT_WAIT_ROOM, READY_BTN]
        self.ui_delay = 0.5
        self.task_switch = True
        self.running = kwargs.get("STOPSIGNAL", None)

    def is_date_valid(self):
        # 获取当前的星期数
        current_weekday = datetime.datetime.now().weekday()
        if current_weekday not in [4, 5, 6]:
            log.insert("5.0", "$今天狩猎战可执行")
            return True
        else:
            log.warning("今天不可执行狩猎战")
            return False

    def loop(self):
        if not self.is_date_valid():  ###判断今天是否可以执行狩猎战
            return
        log.insert("5.0", "$开始狩猎战")
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

    def run(self):  # [FIGHTING, MAIN_ENTRANCE, SECOND_ENTRANCE, HUNT_WAIT_ROOM, READY_BTN, HUNT_END]
        sleep(self.ui_delay)
        match_result = self.ImgRec.match_ui(self.uilist, accuracy=0.8)

        log.insert("2.0", f"Matched UI:{match_result}")
        match match_result:
            case "MAIN_ENTRANCE":
                self.Click.area_click(MAIN_ENTRANCE_CLICK[1])
                log.info(f"@进入主入口 ")
            case "SECOND_ENTRANCE":
                self.Click.area_click(SECOND_ENTRANCE_CLICK[1])
                log.info(f"@进入第二入口 ")
            case "HUNT_WAIT_ROOM":
                self.Click.area_click(HUNT_WAIT_ROOM_CLICK[1])
                log.info(f"@进入狩猎等待室 ")
            case "READY_BTN":
                self.Click.area_click(READY_BTN[1])
                log.info(f"@点击准备按钮 ")
            case "HUNT_VICTORY":
                self.Click.area_click(HUNT_VICTORY[1])
                log.info(f"@successfully 胜利 ")
            case "HUNT_END":
                log.info(f"@狩猎结束 ")
                self.Click.xclick()
                self.task_switch = False
            case "FIGHTING":
                sleep(1)
            case _:
                pass
        pass
        pass

    def set_parms(self, **kwargs):
        pass
