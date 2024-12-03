from task.based.Mytool.Click import Click
from task.based.Mytool.imageRec import ImageRec
from task.based.Mytool.Ocr import Ocr
from task.ltp.res.img_info import *
from time import sleep
from PIGEON.log import log
from task.based.Mytool.Counter import Counter
from random import choices


class Ltp(Click, ImageRec):

    def __init__(self, **kwargs):
        Click.__init__(self)
        ImageRec.__init__(self)
        self.uilist = [fight_ui, main_ui, end_mark_ui, damo_ui, fail_ui]
        self.ui_delay = 0.5
        self.running = kwargs.get("STOPSIGNAL", None)
        self.times = 1
        self.counter = Counter()
        self.fight_again_counter = Counter()

    def get_in_fight(self):
        if res := self.match_img(jg_btn):
            self.area_click(res)
            self.counter.increment()
            self.fight_again_counter.reset()  # 挑战成功，重置挑战次数
            log.insert("2.0", f"开始第{self.counter.count}次寮突破")
            return
        elif self.match_img(ltp_end_ui):
            self.times = 0
            return
        else:
            click_area = choices(
                [[522, 160, 713, 236], [847, 299, 1045, 371], [857, 161, 1036, 240]],
                [0.7, 0.2, 0.1],
            )[0]
            self.area_click(click_area)
        pass

    def challenge_again(self):
        # 挑战失败，重新挑战，最多尝试5次
        self.fight_again_counter.increment()
        if self.fight_again_counter.count > 5:
            self.running.clear()
            log.insert("4.0", f"已经连续{self.fight_again_counter.count}次挑战失败，请求人为介入")
            return
        self.area_click([828, 489, 899, 540])
        sleep(0.5)
        self.area_click([686, 410, 828, 452])
        sleep(1)
        pass

    def run(self):
        sleep(self.ui_delay)
        match_result = self.match_ui(self.uilist, accuracy=0.9)

        log.insert("3.0", f"MATCHED UI:{match_result}")
        match match_result:
            # case 'jg_btn':
            #     self.area_click(self.match_img([jg_btn[0],[587,339,1068,558],'jg_btn']))
            #     #log.debug(f'jg_btn at:{jg_btn_result}')
            #     self.counter.increment()
            #     log.info(f'开始第{self.counter.count}次寮突破')
            case "main_ui":
                self.get_in_fight()
            case "end_mark_ui":
                self.area_click([733, 336, 1198, 644], press_time=0.02, double_click=True)  # double click
            case "damo_ui":
                self.area_click([733, 336, 1198, 644], press_time=0.02, double_click=True)
            case "fight_ui":
                sleep(1)
            case "fail_ui":
                self.challenge_again()
            # case 'ltp_end_ui':self.running.set()
            case _:
                pass
        pass

    def loop(self):
        while self.times:
            if not self.running.is_set():
                break
            self.run()
        pass

    def set_parms(self, **kwargs):
        self.ui_delay = kwargs.get("ui_delay", 0.5)

        pass
