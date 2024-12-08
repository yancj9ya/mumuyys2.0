from task.based.Mytool.Click import Click
from task.based.Mytool.imageRec import ImageRec
from task.based.Mytool.Ocr import Ocr
from task.based.Mytool.Counter import Counter
from task.areademon.res.img_info_auto_create import *
from time import sleep, time, strftime, localtime
from PIGEON.log import log
from random import choices, uniform


class Ad(ImageRec, Click):
    def __init__(self, **values):
        Click.__init__(self)
        ImageRec.__init__(self)
        self.ui_list = [ad_hot, ad_main_ui, challenge_start, ready_btn, challenge_win, challenge_dm]
        self.running = values.get("STOPSIGNAL", True)
        self.challenged_list = [chanllenge_3, chanllenge_2, chanllenge_1]
        self.challenge_start_filter = True
        self.hot_challenge = True
        self.ui_delay = 0.5
        self.stop_task = False
        pass

    def run(self):
        sleep(self.ui_delay)
        res = self.match_ui(self.ui_list)
        log.insert("2.1", f"Matched UI: {res}")
        match res:
            case "ad_main_ui":
                self.area_click(ad_filtrate[1])
            case "ad_hot":
                if self.challenged_list and self.hot_challenge:
                    current_challenge = self.challenged_list.pop()
                    self.hot_challenge = False
                    self.area_click(current_challenge[1])
                else:
                    log.info("No more challenges available.")
                    self.stop_task = True
            case "challenge_start":
                if self.challenge_start_filter:
                    self.area_click(challenge_start[1])
                else:
                    self.area_click(challenge_exit[1])
                    self.challenge_start_filter = True
            case "ready_btn":
                self.area_click(ready_btn[1])
                self.challenge_start_filter = False
                self.hot_challenge = True
            case "challenge_win":
                self.area_click(challenge_win[1])
            case "challenge_dm":
                self.area_click(challenge_dm[1])
                while not self.match_img(challenge_start):
                    self.area_click(challenge_dm[1])
                    sleep(0.5)
            case _:
                pass
        pass

    def loop(self):
        while self.running.is_set():
            self.run()
            if self.stop_task:
                break
        pass

    def set_parms(self, **values):
        self.ui_delay = values.get("ui_delay", 0.5)
        pass
