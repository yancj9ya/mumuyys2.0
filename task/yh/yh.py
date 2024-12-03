from Mytool.Click import Click
from Mytool.imageRec import ImageRec
from Mytool.Ocr import Ocr
from Mytool.Counter import Counter
from img.yh.img_info import *
from time import sleep, time, strftime, localtime
from Mytool.Mylogger import *
from random import choices, uniform


class YH(Click, ImageRec):
    def __init__(self, uilist):
        Click.__init__(self)
        ImageRec.__init__(self)
        self.ui_delay = 0.5
        self.yh_counter = Counter()
        self.uilist = uilist
        self.stop_flag = None
        self.Driver = None

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
            logger.info(f"Driver:{self.Driver}")
        else:
            self.Driver = False
            logger.info(f"Driver:{self.Driver}")

    def run(self):
        sleep(self.random_delay)
        match_res = self.match_ui(self.uilist)
        logger.debug(f"MATCHED UI:{match_res}")
        match match_res:
            case "fight_ui":
                sleep(1)
            case "damo_ui":
                self.random_probability_delay(
                    0.03
                )  # 在100次里面随机3次范围在2-4的长时延迟
                self.area_click([990, 462, 1125, 520])
                self.yh_counter.increment()
                logger.info(f"完成第{self.yh_counter.count}次挑战")
            case "yh_end_mark_ui":
                if uniform(0, 1) <= 0.7:
                    self.double_click([990, 462, 1125, 520])
                else:
                    self.area_click([990, 462, 1125, 520])
            case "yh_end_mark2_ui":
                if uniform(0, 1) <= 0.7:
                    self.double_click([990, 462, 1125, 520])
                else:
                    self.area_click([990, 462, 1125, 520])
            case "room_ui":
                if self.Driver == None:
                    sleep(1)
                    self.room()
                if self.Driver:
                    if res := self.match_color_img(color_tz, color_simi_acc=90):
                        logger.info(f"matched color img:{res}")
                        sleep(0.2)
                        self.area_click(res)
                    else:
                        logger.debug("未匹配到颜色")
                else:
                    sleep(2)


def yh_run(**kw):
    uilist = [fight_ui, damo_ui, yh_end_mark2_ui, yh_end_mark_ui, room_ui]
    yh = YH(uilist)
    yh.stop_flag = kw["stop_event"]
    yh.ui_delay = int(kw["values"]["ui_delay"]) / 1000
    logger.info(f"@ui_delay:{yh.ui_delay}")
    times = int(kw["window"]["timescount"].get()) + 1
    yh.progrees_bar = kw["window"]["jd"].update
    match kw["window"]["yh_dk"].get():
        case True:  # 双开
            logger.info("双开模式")
            yh_n1 = YH(uilist)
            yh_n1.stop_flag = kw["stop_event"]
            yh_n1.ui_delay = int(kw["values"]["ui_delay"]) / 1000
            yh_n1.par_handle = yh_n1.get_handle("#N1 阴阳师 - MuMu模拟器12")
            yh_n1.child_handle = yh_n1.get_handleEx(yh_n1.par_handle, "MuMuPlayer")
            while yh.yh_counter.count < times and not yh.stop_flag.is_set():
                yh.run()
                yh_n1.run()
                yh.progrees_bar(value=f"进度 {yh.yh_counter.count}/{times-1}")
        case False:  # 单开
            logger.info("单开模式")
            while yh.yh_counter.count < times and not yh.stop_flag.is_set():
                yh.run()
                yh.progrees_bar(value=f"进度 {yh.yh_counter.count}/{times-1}")
