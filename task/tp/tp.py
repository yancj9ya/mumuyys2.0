from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec
from tool.Mytool.Ocr import Ocr
from tool.Mytool.Counter import Counter
from tool.based.base.res.base_img import *
from task.tp.res.img_info import *
from task.tp.res.img_info_auto_create import *
from time import sleep, time, strftime, localtime
from PIGEON.log import Log
from random import shuffle
from win11toast import toast

log = Log()


class Tp(Click, ImageRec):
    def __init__(self, **kwargs):
        Click.__init__(self)
        ImageRec.__init__(self)
        self.uilist = [FIGHTING, DAMO369, damo_ui, tp_main_ui, end_mark_ui, fail_ui]
        self.keep_57_flag = False
        self.task_switch = True
        self.ocr = Ocr()
        self.counter = Counter("tp")
        self.quit_count = Counter("tp_quit_count")
        self.fight_again_counter = Counter("tp_fight_again_count")
        self.running = kwargs.get("STOPSIGNAL", None)
        self.ui_delay = 0.5
        self.tp_jg_area = [
            (249, 155, 459, 248),
            (577, 153, 791, 259),
            (903, 153, 1123, 257),
            (238, 290, 463, 399),
            (580, 287, 793, 389),
            (904, 286, 1123, 394),
            (243, 423, 459, 526),
            (567, 425, 793, 529),
            (909, 425, 1123, 527),
        ]
        shuffle(self.tp_jg_area)  # 随机打乱顺序

    def quit_to_keep(self, area):

        log.info(f"start quit_to_keep on 57")
        self.quit_count.reset()
        while True:
            if not self.running.is_set():
                return
            if self.match_img(tp_main_ui):
                self.area_click(area)
                sleep(0.4)
            if jg := self.match_img(btn_jg):
                self.area_click(jg)
                sleep(0.3)
            if quit_btn := self.match_img(tp_quit_ui):
                self.area_click(quit_btn)
                sleep(0.2)
            if btn_sure_quit_r := self.match_img(btn_sure_quit):
                self.area_click(btn_sure_quit_r)
                sleep(2)
            if self.match_img(fail_ui):
                # self.area_click(quit_fail)
                self.challenge_again()
                self.quit_count.increment(interval=3)
                log.info(f"quit_count:{self.quit_count.count}")
                if self.quit_count.count == 4:
                    log.info(f"quit_count:end")
                    sleep(3)
                    return
                sleep(0.2)

    def tp_main_ui(self):
        for area in self.tp_jg_area:
            sleep(0.1)
            if not self.running.is_set():
                return
            if not self.match_img((have_po[0], area)):
                # 退结界判断
                if self.keep_57_flag:
                    res = self.match_duo_img((have_po[0], [371, 144, 1132, 535]))
                    log.insert("3.1", f"目前版面：{len(res)}/9")
                    if len(res) == 8:
                        self.quit_to_keep(area)
                        return  # 直接返回uimatch，避免战斗的点击标记
                self.area_click(area, press_time=0.1)
                sleep(0.7)
                # 根据区域缩小进攻按钮的寻找范围，像素位移(249,262)
                if jg := self.match_img(
                    [
                        btn_jg[0],
                        [area[0], area[1], area[0] + 249, area[1] + 262],
                        area[2],
                    ],
                    accuracy=0.9,
                ):
                    self.area_click(jg)
                    self.fight_again_counter.reset()  # 挑战成功，重置挑战次数
                    sleep(1)
                    self.tp_jg_area = self.tp_jg_area[1:] + [area]
                    return
            self.tp_jg_area = self.tp_jg_area[1:] + [area]

    def challenge_again(self):
        # 挑战失败，重新挑战，最多尝试5次
        self.fight_again_counter.increment()
        if self.fight_again_counter.count > 5:
            self.stop_flag.set()
            log.info(f"已经连续{self.fight_again_counter.count}次挑战失败，请求人为介入")
            toast("已经连续5次挑战失败，请人为介入")
            return
        self.area_click([828, 489, 899, 540])
        sleep(0.5)
        self.area_click([686, 410, 828, 452])
        sleep(1)

    def stat_award(self):
        """重写"""
        pass

    def run(self):
        sleep(self.ui_delay)
        match_result = self.match_ui(self.uilist)
        log.insert("2.1", f"Matched UI:{match_result}")
        match match_result:
            case "FIGHTING":
                sleep(1)
            case "tp_main_ui":
                if self.counter.compare(self.times):
                    self.task_switch = False
                    return
                self.tp_main_ui()
            case "damo_ui" | "DAMO369":
                self.stat_award()
                self.counter.increment()
                log.info(f"第{self.counter.count}次突破进攻Done！")
                self.area_click(damo_ui[1])
                sleep(0.5)
                self.area_click([990, 462, 1125, 520])
            case "end_mark_ui":
                self.area_click([990, 462, 1125, 520])
            case "fail_ui":
                self.challenge_again()
            case _:
                pass

    def loop(self):
        if ocr_result := Ocr.ocr([1138, 12, 1234, 48]):
            if ocr_result[1] > 0.8:
                self.times = int(ocr_result[0].split("/")[0])
                log.info(f"突破卷：{self.times}")
            else:
                self.times = 0
        while self.task_switch:
            # print(f"state:{self.running.state}")
            match self.running.state:
                case "RUNNING":
                    self.run()
                    log.insert("5.1", f"突破进度 {self.counter.count}/{self.times}")
                case "STOP":
                    log.insert("2.1", f"@任务已停止 ")
                    self.counter.reset()
                    return
                case "WAIT":
                    sleep(1)
                    continue
                case _:
                    pass

    def set_parms(self, **kwargs):
        self.keep_57_flag = kwargs.get("tp_keep_level", True)
        self.ui_delay = float(kwargs.get("ui_delay", 0.5))
