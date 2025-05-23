from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec
from tool.Mytool.Ocr import Ocr
from tool.Mytool.Counter import Counter
from tool.based.base.res.base_img import *
from task.yh.res.img_info import *
from time import sleep, time, strftime, localtime
from PIGEON.log import log
from random import choices, uniform


class Yh(Click, ImageRec):
    def __init__(self, **values):
        Click.__init__(self)
        ImageRec.__init__(self)
        self.ui_delay = 0.5
        self.yh_counter = Counter()
        self.uilist = [FIGHTING, damo_ui, yh_end_mark2_ui, yh_end_mark_ui, room_ui, accept_gear]
        self.running = values.get("STOPSIGNAL", True)
        self.Driver = None
        self.times = 0

    # 概率性的长时延迟
    def random_probability_delay(self, probability):
        if uniform(0, 1) <= probability:
            sleep(uniform(2, 4))
        else:
            return

    def double_click(self, pos: list):
        self.area_click(pos)
        sleep(0.1)
        self.area_click(pos)

    @property
    def random_delay(self):
        match self.yh_counter.count:
            case x if x < 100:
                return round(uniform(0, 0.5), 2)
            case x if 100 <= x < 300:
                return round(uniform(0.5, 1), 2)
            case x if 300 <= x:
                return round(uniform(1, 1.7), 2)
        pass

    def room(self):
        if res := self.match_img(color_tz):
            self.Driver = True
            log.insert("5.1", f"Driver:{self.Driver}")
        else:
            self.Driver = False
            log.insert("5.1", f"Driver:{self.Driver}")

    def run(self):
        sleep(self.random_delay)
        match_res = self.match_ui(self.uilist)
        log.insert("2.1", f"MATCHED UI:{match_res}")
        match match_res:
            case "FIGHTING":
                sleep(1)
            case "damo_ui":
                self.random_probability_delay(0.03)  # 在100次里面随机3次范围在2-4的长时延迟
                self.area_click([990, 462, 1125, 520])
                log.insert("3.1", f"完成第{self.yh_counter.count}次挑战")
            case "yh_end_mark_ui" | "yh_end_mark2_ui":
                self.yh_counter.increment(13)
                if uniform(0, 1) <= 0.7:
                    self.double_click([990, 462, 1125, 520])
                else:
                    self.area_click([990, 462, 1125, 520])
            case "room_ui":
                if self.Driver == None:
                    sleep(1)
                    self.room()
                if self.Driver:
                    if res := self.match_color_img_by_hist(color_tz):
                        log.debug(f"Color image matched")
                        sleep(0.2)
                        self.area_click(res)
                        # self.yh_counter.increment()
                        log.insert("3.1", f"进行第{self.yh_counter.count}次挑战")
                else:
                    sleep(2)
            case "accept_gear":
                self.area_click(accept_gear[1], double_click=True)
                self.uilist.remove(accept_gear)

    def loop(self):
        log.insert("4.1", f"开始循环，次数：{self.times}")
        while self.yh_counter.count < self.times:
            match self.running.state:
                case "RUNNING":
                    self.run()
                    log.insert("4.1", f"进度 {self.yh_counter.count}/{self.times}")
                case "STOP":
                    log.insert("2.1", f"@任务已停止 ")
                    self.yh_counter.reset()
                    return
                case "WAIT":
                    sleep(1)
                    continue
                case _:
                    pass

    def set_parms(self, **values):
        self.times = int(values.get("times", 0))
        self.ui_delay = values.get("ui_delay", 0.5)
        self.yh_counter.reset()
