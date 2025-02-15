from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec
from tool.Mytool.Ocr import Ocr
from tool.Mytool.Counter import Counter
from task.yqfy.res.img_info import *
from time import sleep, time, strftime, localtime
from PIGEON.log import log
from random import choices, uniform


class YQFY(Click, ImageRec):
    def __init__(self, uilist):
        Click.__init__(self)
        ImageRec.__init__(self)
        self.ui_delay = 0.2
        self.counter = Counter()
        self.uilist = uilist
        self.stop_flag = None

    def home_ui(self):
        home_match = self.match_ui([access_ui, in_queue_ui, home_ui])
        match home_match:
            case "in_queue_ui":
                sleep(1)
            case "home_ui":
                self.area_click(home_ui[1])
            case _:
                pass
        pass

    def run(self):
        sleep(self.ui_delay)
        match_res = self.match_ui(self.uilist)
        log.insert("2.1", f"MATCHED UI:{match_res}")
        match match_res:
            case "access_ui":
                self.area_click(access_ui[1])
                sleep(0.8)
            case "home_ui":
                self.home_ui()
            case "yqfy_ui":
                self.area_click([716, 609, 855, 639])
            case "sl_ui" | "damo_ui":
                self.area_click([872, 381, 1224, 642])
            case _:
                sleep(0.1)


def yqfy_run(**kw):

    uilist = [access_ui, home_ui, yqfy_ui, sl_ui, damo_ui]
    yqfy = YQFY(uilist)
    yqfy.stop_flag = kw["stop_event"]
    while not yqfy.stop_flag.is_set():
        yqfy.run()
