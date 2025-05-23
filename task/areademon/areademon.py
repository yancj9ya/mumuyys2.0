from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec
from tool.Mytool.Ocr import Ocr
from tool.Mytool.Counter import Counter
from task.areademon.res.img_info_auto_create import *
from tool.based.base.res.base_img import FIGHTING
from time import sleep, time, strftime, localtime
from PIGEON.log import log
from random import choices, uniform


class Ad(ImageRec, Click):
    def __init__(self, **values):
        Click.__init__(self)
        ImageRec.__init__(self)
        self.ui_list = [FIGHTING, ad_hot, ad_main_ui, challenge_start, ready_btn, challenge_win, challenge_dm, BATTLE__FAIL]
        self.running = values.get("STOPSIGNAL", True)
        self.challenged_list = {tuple(chanllenge_3[1]): False, tuple(chanllenge_2[1]): False, tuple(chanllenge_1[1]): False}
        self.challenge_start_filter = True
        self.ui_delay = 0.5
        self.stop_task = False
        self.mode = "extra"
        pass

    def chose_challenge(self):
        for chanllge, state in self.challenged_list.items():
            if not state:
                return chanllge
        return None

    def select_mode(self, mode: str):
        is_extra = not self.match_img(EXTRA)
        if (is_extra and mode == "extra") or (not is_extra and mode == "normal"):
            return
        else:
            self.area_click(EXTRA[1])
            sleep(0.5)
            log.debug(f"切换模式: {mode}")

    def run(self):
        sleep(self.ui_delay)
        res = self.match_ui(self.ui_list)
        log.insert("2.1", f"Matched UI: {res}")
        match res:
            case "FIGHTING":
                sleep(1)
            case "ad_main_ui":
                self.area_click(ad_filtrate[1])
            case "ad_hot":
                # 点击热门
                self.area_click(ad_hot[1])
                sleep(0.3)
                # 获取挑战对象
                self.current_challenge = self.chose_challenge()
                if self.current_challenge:
                    self.area_click(self.current_challenge)
                else:
                    log.info(f"no more challenge")
                    # log.info(f"{self.challenged_list} and {self.hot_challenge}")
                    self.stop_task = True
            case "challenge_start":
                self.select_mode(self.mode)
                if self.challenge_start_filter:
                    self.area_click(challenge_start[1])
                else:
                    self.area_click(challenge_exit[1])
                    self.challenge_start_filter = True
            case "ready_btn":
                self.area_click(ready_btn[1])
                self.challenge_start_filter = False
                self.challenged_list[self.current_challenge] = True
            case "challenge_win":
                self.area_click(challenge_win[1])
            case "challenge_dm":
                self.area_click(challenge_dm[1])
                while not self.match_img(challenge_start):
                    self.area_click(challenge_dm[1])
                    sleep(0.5)
            case "BATTLE__FAIL":  # 战斗失败,重新挑战
                self.area_click(BATTLE__FAIL[1])
                sleep(0.5)
                self.area_click(RE_CHALLENGE_CONFIRM)
            case _:
                pass
        pass

    def loop(self):
        while not self.stop_task:
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

    def set_parms(self, **values):
        self.ui_delay = float(values.get("ui_delay", 0.5))
        self.mode = values.get("mode", "extra")
        pass
