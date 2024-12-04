from task.based.Mytool.Click import Click
from task.based.Mytool.imageRec import ImageRec
from task.based.Mytool.Ocr import Ocr
from task.based.Mytool.Counter import Counter
from task.hd.res.img_info import *
from time import sleep, time, strftime, localtime
from PIGEON.log import log
from random import choices, uniform


class Hd(Click, ImageRec):
    def __init__(self, **kwargs):
        Click.__init__(self)
        ImageRec.__init__(self)
        self.BTN_TZ = None
        self.ui_delay = 0.5
        self.hd_counter = Counter()
        self.uilist = [fight_ui, damo_ui, end_mark_ui, sl_ui, end_999_hdyh_ui, ready_ui]
        self.running = kwargs.get("STOPSIGNAL", True)
        self.times = 0

    # 寻找按钮并且识别次数
    def find_btn_tz(self):
        if btn_res := self.find_duo_img("task/hd/res/btn", [672, 266, 1260, 701], return_only_one=True):
            self.BTN_TZ = btn_res[0:2] + ["btn_tz"]
            log.info(f"找到按钮：{btn_res}")
            self.uilist.append(self.BTN_TZ)
            log.info(f"按钮添加到ui列表：{self.BTN_TZ}")
            match btn_res[2]:
                case "btn_yyh":
                    log.insert("5.1", f"识别模式：业原火")
                    if ocr_res := Ocr.ocr([754, 23, 809, 60]):
                        if ocr_res[1] > 0.9:
                            self.times = int(ocr_res[0])
                            log.info(f"挑战次数为{self.times}")

                case "btn_mw":
                    log.insert("5.1", f"识别模式：秘闻挑战")
                    self.times = 11
                case "btn_yl":
                    log.insert("5.1", f"识别模式：御灵挑战")
                case _:
                    log.insert("5.1", f"识别模式：版本活动")
                    pass
        else:
            log.info("未找到按钮")

    @property
    def random_delay(self):
        match self.hd_counter.count:
            case x if x < 100:
                return round(uniform(0, 0.5), 2)
            case x if 100 <= x < 300:
                return round(uniform(0.5, 1), 2)
            case x if 300 <= x:
                return round(uniform(1, 1.7), 2)
        pass

    def random_duo_area_click(self, rect_list, weight_list, click_twice=False):
        if len(rect_list) != len(weight_list):
            log.info("rect_list与weight_list长度不一致")
            return
        click_area = choices(rect_list, weight_list)[0]
        if click_twice:
            self.area_click(click_area, press_time=0.1)
            sleep(0.1)
            self.area_click(click_area, press_time=0.1)
        else:
            self.area_click(click_area)

    # 概率性的长时延迟
    def random_probability_delay(self, probability):
        if uniform(0, 1) <= probability:
            sleep(uniform(2, 4))
        else:
            return

    def run(self):
        if self.BTN_TZ is None:
            self.find_btn_tz()
        sleep(self.ui_delay + self.random_delay)
        match_res = self.match_ui(self.uilist)
        log.insert("2.1", f"Matched UI: {match_res}")
        match match_res:
            case "fight_ui":
                sleep(1)
            case "damo_ui":
                self.random_probability_delay(0.03)  # 在100次里面随机3次范围在2-4的长时延迟
                self.area_click([990, 462, 1125, 520])
            case "sl_ui":
                self.random_probability_delay(0.03)
                rect_list = [(816, 282, 1236, 672), (490, 601, 766, 683)]
                weight_list = [8, 2]
                self.random_duo_area_click(rect_list, weight_list)
            case "end_mark_ui":
                self.area_click([990, 462, 1125, 520])
            case "btn_tz":
                self.area_click(self.BTN_TZ[1])
                self.hd_counter.increment()
                log.insert("3.1", f"开始第{self.hd_counter.count}次挑战")
            case "end_999_hdyh_ui":
                sleep(self.random_delay)
                rect_list = [
                    (1014, 216, 1254, 641),
                    (488, 528, 1219, 697),
                    (79, 334, 299, 628),
                ]
                weight_list = [6, 3.5, 0.5]
                self.random_duo_area_click(rect_list, weight_list, click_twice=True)
            case "ready_ui":
                self.area_click([1134, 551, 1227, 621])

    def loop(self):
        while self.hd_counter.count < self.times and self.running.is_set():
            self.run()
            log.insert("4.1", f"进度: {self.hd_counter.count}/{self.times}")
        pass

    def set_parms(self, **kwargs):
        self.ui_delay = int(kwargs.get("ui_delay", 0.5))
        self.times = int(kwargs.get("times", 0))
        pass
