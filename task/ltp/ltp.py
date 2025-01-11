from task.based.Mytool.Click import Click
from task.based.Mytool.imageRec import ImageRec
from task.based.Mytool.Ocr import Ocr
from task.based.base.res.base_img import *
from task.ltp.res.img_info import *
from time import sleep
from PIGEON.log import log
from task.based.Mytool.Counter import Counter
from random import choices
from time import time
from win11toast import toast


class Ltp(Click, ImageRec):

    def __init__(self, **kwargs):
        Click.__init__(self)
        ImageRec.__init__(self)
        self.uilist = [FIGHTING, main_ui, damo_ui, end_mark_ui, fail_ui]
        self.ui_delay = 0.5
        self.running = kwargs.get("STOPSIGNAL", None)
        self.times = 1
        self.counter = Counter()
        self.fight_again_counter = Counter()
        self.reward_dict = {}

    def get_in_fight(self):
        if res := self.match_img(jg_btn):
            self.area_click(res)
            self.counter.increment()
            self.fight_again_counter.reset()  # 挑战成功，重置挑战次数
            log.insert("3.0", f"开始第{self.counter.count}次寮突破")
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
            self.times = 0
            log.info(f"已经连续{self.fight_again_counter.count}次挑战失败，请求人为介入")
            toast("已经连续5次挑战失败，请人为介入")
            return
        self.area_click([828, 489, 899, 540])
        sleep(0.5)
        self.area_click([686, 410, 828, 452])
        sleep(1)
        pass

    def run(self):
        sleep(self.ui_delay)
        match_result = self.match_ui(self.uilist, accuracy=0.9)

        log.insert("2.0", f"Matched UI:{match_result}")
        match match_result:
            case "main_ui":
                self.get_in_fight()
            case "end_mark_ui":
                self.area_click([733, 336, 1198, 644], press_time=0.02)  # double click
            case "damo_ui":
                self.reward_confirm()
                self.area_click([733, 336, 1198, 644], press_time=0.02, double_click=True)
            case "FIGHTING":
                sleep(1)
            case "fail_ui":
                self.challenge_again()
            # case 'ltp_end_ui':self.running.set()
            case _:
                pass
        pass

    def reward_confirm(self):
        if not hasattr(self, "time_reward"):
            self.time_reward = time()
            log.debug(f"time_reward set")
        elif time() - self.time_reward > 5:
            self.time_reward = time()
            k_to_t = {"blue_t": "蓝票", "m_hj": "中", "s_hj": "小", "b_hj": "大", "jjk": "结界卡"}
            award_str = " "
            sleep(0.5)
            if res := self.stat_reward("task/ltp/res/reward", [156, 132, 1099, 553]):
                for reward in res.keys():
                    # log.info(reward)
                    if reward not in self.reward_dict:
                        self.reward_dict[reward] = 1
                    else:
                        self.reward_dict[reward] += 1
                log.info(f"*" * 16)
                for key, value in self.reward_dict.items():
                    log.info(f" {key:^10}: {value:^2}")
                    award_str += f"{k_to_t[key]}x{value} "
                log.info(f"*" * 16)
                log.insert("4.0", f"{award_str}")

    def loop(self):
        log.insert("5.0", "$开始寮突破")
        while self.times:
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

    def set_parms(self, **kwargs):
        self.ui_delay = float(kwargs.get("ui_delay", 0.5))

        pass
