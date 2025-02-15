# 逢魔之魂
from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec
from tool.Mytool.Ocr import Ocr
from tool.Mytool.Counter import Counter
from task.fm.res.img_info_auto_create import *
from time import sleep, time, strftime, localtime
from datetime import datetime
from PIGEON.log import log
from random import choices, uniform


class Fm(Click, ImageRec):
    def __init__(self, **kwargs):
        Click.__init__(self)
        ImageRec.__init__(self)
        self.uilist = [FIGHTING, ready_btn, fm_page_ui, wait_start, end_battle, battle_sl, damo_ui]
        self.running = kwargs.get("STOPSIGNAL", None)
        self.has_4_pack_opened = False
        self.task_switch = True
        self.ui_delay = 0.5

    def set_parms(self, **parms):
        self.ui_delay = float(parms.get("ui_delay", 0.5))

        pass

    def loop(self):

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

    def run(self):
        sleep(self.ui_delay)
        res = self.match_ui(self.uilist)
        log.insert("2.1", f"UI match: {res} ")
        match res:
            case "fm_page_ui":
                if not self.has_4_pack_opened:
                    self.open_pack()
                else:
                    self.enter_fm()
            case "wait_start" | "in_battle":
                sleep(1)
            case "end_battle":
                self.end_battle()
            case "ready_btn":
                self.area_click(ready_btn[1])
            case "battle_sl":
                self.area_click(battle_sl[1])
            case "damo_ui":
                self.area_click(damo_ui[1])
            case "FIGHTING":
                sleep(1)
            case _:
                pass
        pass

    def open_pack(self):
        if not self.match_img(red_egg_done) and self.match_img(FOURTH_BOX):
            self.area_click(real_fm[1])
            sleep(4)
        elif not self.match_img(red_egg_done) and not self.match_img(FOURTH_BOX):
            self.area_click(red_egg[1])
        else:
            self.has_4_pack_opened = True

    def enter_fm(self):
        if self.match_img(hard_boss, accuracy=0.8):
            self.area_click(hard_boss[1], double_click=True)
            sleep(1)
            if self.match_img(BOSS_SIGN):
                self.area_click(center_entrance[1])
            sleep(1)
            if self.match_img(confirm_hard_boss):
                self.area_click(confirm_hard_boss[1])
        elif self.match_img(normal_boss):
            self.area_click(normal_boss[1], double_click=True)
            sleep(1)
            if self.match_img(BOSS_SIGN):
                self.area_click(center_entrance[1])
            sleep(1)
            if self.match_img(confirm_boss):
                self.area_click(confirm_boss[1])

    def end_battle(self):
        if self.match_img(back):
            self.area_click(back[1])
            sleep(1)
        if self.match_img(back_confirm):
            self.area_click(back_confirm[1])
            self.task_switch = False
        pass
