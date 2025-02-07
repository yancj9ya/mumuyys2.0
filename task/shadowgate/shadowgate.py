from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec
from tool.based.base.res.base_img import *
from task.shadowgate.res.img_info_auto_create import *
from time import sleep
from PIGEON.log import log
import datetime


class ShadowGate:

    def __init__(self, **kwargs):
        self.Click = Click()
        self.ImgRec = ImageRec()
        self.uilist = [
            FIGHTING,
            shadow_gate_page,
            challenge_confirm_btn,
            shadow_gate_challenge,
            shadow_gate_room,
            ready_btn,
            victory,
        ]
        self.ui_delay = 0.5
        self.task_switch = True
        self.running = kwargs.get("STOPSIGNAL", None)

    def is_date_valid(self):
        # 获取当前的星期数
        current_weekday = datetime.datetime.now().weekday()
        if current_weekday in [4, 5, 6]:
            log.insert("5.0", "$今天可执行阴界之门")
            return True
        else:
            log.warning("今天不可执行阴界之门")
            return False

    def loop(self):
        if not self.is_date_valid():  ###判断今天是否可以执行阴界之门
            return
        log.insert("5.0", "$开始阴界之门")
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

    def run(self):
        sleep(self.ui_delay)
        match_result = self.ImgRec.match_ui(self.uilist, accuracy=0.8)

        log.insert("2.0", f"Matched UI:{match_result}")
        match match_result:
            case "shadow_gate_page":
                self.Click.area_click(shadow_gate_page[1])
            case "challenge_confirm_btn":
                self.Click.area_click(challenge_confirm_btn[1])
            case "shadow_gate_challenge":
                self.Click.area_click(challenge_btn[1])
            case "shadow_gate_room":
                self.Click.area_click(room_challenge_btn[1])
            case "ready_btn":
                self.Click.area_click(ready_btn[1])
            case "victory":
                self.Click.area_click(victory[1])
                self.task_switch = False
            case "FIGHTING":
                sleep(1)
            case _:
                pass
        pass
        pass

    def set_parms(self, **kwargs):
        pass
