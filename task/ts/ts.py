from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec
from tool.Mytool.Ocr import Ocr
from tool.Mytool.Counter import Counter
from task.ts.res.img_info import *
from time import sleep, time, strftime, localtime
from PIGEON.log import log


from task.tp.tp import Tp
from random import choices


class Ts(Click, ImageRec):
    def __init__(self, **values):
        from page.page_switch import nav

        Click.__init__(self)
        ImageRec.__init__(self)
        self.monster_counter = Counter(name="monster")
        self.tp_ticket_count = Counter(name="tp_ticket")
        self.uilist = [ts_main_box, ts_main_ui, ts_tz_ui, ts_cm_ui, damo_ui, ts_end_mark_ui]
        self.ui_delay = 0.5
        self.reward_dict = {}
        self.last_monster = None
        self.running = values.get("STOPSIGNAL", True)
        self.tp_ticket_limit = 27
        self.monster_limit = 200
        self.switch_ui = nav

    def exit_once(self):
        self.area_click([34, 42, 69, 81])  # 点击退出按钮
        sleep(0.8)
        self.area_click([718, 389, 823, 415])  # 点击确认退出按钮

    def find_m(self):
        if res := self.match_img(ts_cm_boss_btn):
            self.monster_counter.increment()
            log.insert("3.1", f" monster_counter[boss]:{self.monster_counter.count}")
            self.area_click(res)  # 找到BOSS怪
            self.last_monster = "boss"
            return
        elif res := self.match_img(ts_cm_normal_btn, accuracy=0.8):
            self.monster_counter.increment()
            log.insert("3.1", f" monster_counter:{self.monster_counter.count}")
            self.area_click(res)  # 找到普通怪
            self.last_monster = "normal"
            return
        elif self.last_monster == "boss":
            self.exit_once()  # 结束战斗
            log.info(f'{"*"*20}Quit')
        elif self.last_monster == "normal":  # 找不到Next怪，向右走
            log.debug(f"@No found，head toward")
            match choices(["slide", "click"], weights=[0.8, 0.2], k=1)[0]:
                case "slide":
                    log.info(f"@slide to right")
                    self.slide([1162, 146, 1226, 203], [231, 133, 301, 199])
                case "click":
                    log.info(f"@click walk to right")
                    self.area_click([920, 498, 1251, 579])  # 找不到怪，向前走
                    sleep(1.5)  # 等待1.5秒

    def reward_confirm(self):

        k_to_t = {"blue_t": "蓝票", "m_hj": "中", "s_hj": "小", "b_hj": "大", "tp_ticket": "突破卷"}
        award_str = " "
        # sleep(0.5)
        if res := self.stat_reward("task/ts/res/reward", [256, 156, 1100, 449]):
            for reward in res.keys():
                # log.info(reward)
                if reward not in self.reward_dict:
                    self.reward_dict[reward] = 1
                else:
                    self.reward_dict[reward] += 1
            log.info(f"*" * 16)
            for key, value in self.reward_dict.items():
                log.info(f"*{key:^10}: {value:^2}*")
                award_str += f"{k_to_t[key]}x{value} "
            log.info(f"*" * 16)
            log.insert("4.1", f"{award_str}")
            if "tp_ticket" in res.keys():
                self.tp_ticket_count.count += 1
                log.insert("5.1", f" tp_ticket_count:{self.tp_ticket_count.count}")

    def run(self):
        sleep(self.ui_delay)
        ui_serch_result = self.match_ui(self.uilist)
        log.insert("2.1", f" Matched ui:{ui_serch_result}")
        match ui_serch_result:
            case "ts_main_box":
                self.switch_ui.switch_to("EXPLORE", self.running)  # 先切换到探索主界面
                if box_cor := self.match_img(ts_main_box):
                    self.area_click(box_cor)  # 点击box
            case "ts_main_ui":
                self.area_click([1081, 504, 1208, 572])
            case "ts_tz_ui":
                self.area_click(ts_tz_ui[1])
                self.last_monster = None
            case "ts_cm_ui":
                self.find_m()
            case "ts_end_mark_ui":
                self.area_click([990, 462, 1125, 520])
            case "damo_ui":
                sleep(0.5)
                self.reward_confirm()
                self.area_click([990, 462, 1125, 520])
                sleep(0.5)
                self.area_click([990, 462, 1125, 520])

            case _:
                sleep(1)

    def loop(self):
        print(f'ts_loop start at {strftime("%Y-%m-%d %H:%M:%S", localtime())}')
        # current_task = "TP"
        while all([self.monster_counter.count < self.monster_limit, self.running.is_set()]):
            print(f"current_task:{self.current_task}")
            match self.current_task:
                case "TP":
                    log.info(f"开始突破...")
                    if self.switch_ui.switch_to("ENCHANTMENT_1", self.running):  # 切换到突破主界面
                        log.insert("3.1", f"{' 突破进行中...':<27}")
                        self.tp.task_switch = True  # 开启TP任务
                        self.tp.loop()  # 进入TP界面
                        self.tp.counter.reset()  # 重置TP次数
                        self.tp_ticket_count.reset()  # 重置TP票数
                        self.current_task = "TS"
                case "TS":
                    if self.switch_ui.switch_to("EXPLORE", self.running):
                        log.info(f"开始探索...")  # 切换到探索主界面
                        while all([self.tp_ticket_count.count < self.tp_ticket_limit, self.monster_counter.count < self.monster_limit, self.running.is_set()]):
                            self.run()
                        self.current_task = "TP"

    def set_parms(self, **values):
        self.ui_delay = values.get("ui_delay", 0.5)
        if values.get("with_tp", True):
            self.current_task = "TP"
            self.tp_ticket_limit = values.get("tp_ticket_limit", 27)
        else:
            self.current_task = "TS"
            self.tp_ticket_limit = 100000
        self.monster_limit = values.get("monster_limit", 200)

        # create tp instance
        self.tp = Tp(STOPSIGNAL=self.running)
        self.tp.set_parms(ui_delay=values.get("ui_delay", 0.5))
        self.tp.stat_award = self.reward_confirm
        log.debug(f"set_parms: \n突破卷限制{self.tp_ticket_limit} \n怪物限制{self.monster_limit}")
        pass
