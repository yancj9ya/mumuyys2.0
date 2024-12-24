from task.based.Mytool.Click import Click
from task.based.Mytool.imageRec import ImageRec
from task.based.Mytool.Ocr import Ocr
from task.jy.res.img_info_auto_create import *
from time import sleep
from PIGEON.log import log
from PIGEON.retry import retry
from task.based.Mytool.Counter import Counter
from random import choices
from time import time
import re


class Jy(Click, ImageRec):
    def __init__(self, **kwargs):
        Click.__init__(self)
        ImageRec.__init__(self)
        self.ui_delay = 0.5
        self.ocr = Ocr()
        self.uilist = [jy_main_ui, yc_page, self_ward]
        self.has_refreshed = False
        self.max_number = 0
        self.left_max = 0
        self.right_max = 0

    def loop(self):
        while True:
            self.run()
            if hasattr(self, "next_time"):
                break

    def set_parms(self, *args, **kwargs):
        pass

    @retry(max_retries=5, delay=1, exceptions=(Exception,))
    def get_right_jj_num(self):
        """获取右边的太鼓的数量"""
        ocr_res = self.ocr.ocr((795, 425, 977, 453))
        log.info(f"OCR result: {ocr_res[0]}")
        if ocr_res[1] > 0.6:
            hand_res_str = re.sub(r"[^a-zA-Z0-9]", "", ocr_res[0])
            return int(hand_res_str)
        else:
            raise Exception("Failed to get right JJ number")
        sleep(1)  # Add a small delay to avoid infinite looping

    def re_serch(self):
        temp_num_list = []
        sleep(1)
        six_star = self.match_duo_img(six_star_img, 0.8)
        five_star = self.match_duo_img(five_star_img, 0.8)
        log.info(f"Found 6-star: {len(six_star)}, 5-star: {len(five_star)}")
        rec_list = six_star + five_star if six_star and five_star else six_star or five_star

        try:
            for area in rec_list:
                log.info(f"found {len(rec_list)} target in this page")
                self.area_click(area)
                sleep(1)
                temp_num = self.get_right_jj_num()
                if temp_num:
                    if temp_num == 76 or (hasattr(self, "finally_number") and temp_num == self.finally_number):
                        self.get_in_to_jy()
                        self.finally_number = temp_num
                        self.next_time = "06:00:00"
                        return "success"
                    temp_num_list.append(temp_num)
                    log.info(f"Found JJ number: {temp_num}")
            return max(temp_num_list) if temp_num_list else None
        except Exception as e:
            log.error(f"Error in re_serch: {e}")
            return None
        finally:
            self.slide((517, 580), (557, 200), move_time=1)

    def refresh_jy_list(self):
        log.info("Refreshing JY list...")
        if not self.has_refreshed:
            sleep(0.5)
            self.slide((190, 191), (195, 560), move_time=1)  # 下拉刷新同区好友
            self.area_click(diff_server_seat[1])
            sleep(0.5)
            self.slide((190, 191), (195, 560), move_time=1)  # 下拉刷新跨区好友
            self.area_click(same_server_seat[1])
            sleep(0.5)
            self.has_refreshed = True
        else:
            log.info("Already refreshed")
        sleep(1)

    def find_max_number(self, area_type):
        """Find the max number from a given area (left or right)."""
        self.area_click(area_type[1], double_click=True, double_click_time=0.2)
        sleep(0.5)
        log.info(f"Finding max number in {area_type[-1]}...")
        for _ in range(5):
            if serch_max_num := self.re_serch():
                if isinstance(serch_max_num, int):
                    if area_type == same_server_seat:
                        self.left_max = max(self.left_max, serch_max_num)
                    else:
                        self.right_max = max(self.right_max, serch_max_num)

                elif isinstance(serch_max_num, str):
                    return
        sleep(0.5)

    def get_in_to_jy(self):
        confirm_jy_success = False
        while not confirm_jy_success:
            sleep(0.5)
            if self.match_img(enter_jy):
                self.area_click(enter_jy[1])
                log.info("Enter JY page")
            if self.match_img(jy_sure_page):
                if self.match_img(red_damo):
                    self.area_click(red_damo[1])
                    log.info("Red damo")
                if self.match_img(confirm_jy_btn):
                    sleep(0.5)
                    self.area_click(confirm_jy_btn[1])
                    log.info("Confirm JY")
                    confirm_jy_success = True
                    log.info("Set confirm_jy_success to True")
            else:
                self.area_click([630, 309, 648, 385])
                log.info("Click center of JY page")
        while True:
            if self.match_img(confirm_jy_btn):
                self.area_click(confirm_jy_btn[1])
            if self.match_img(exit_jy_page):
                self.area_click(exit_jy_page[1])
                sleep(1)
            if self.match_img(self_ward):
                self.next_time = "06:00:00"
                log.info(f"confirm_jy_success,Next time: {self.next_time}")
                break
        sleep(1)

    def ward_yc(self):
        res = self.match_img(blank_seat_2)
        log.info(f"Blank seat 2: {res}")
        if res:
            self.area_click(blank_seat_2[1])
            sleep(0.5)
        else:
            self.next_time = self.get_jyh_end_time()
            self.area_click(exit_jy_page[1])

    def get_jyh_end_time(self):
        pattern = r"^[0][0-5]:[0-5][0-9]:[0-5][0-9]$"
        while True:
            sleep(1)
            if res := self.ocr.ocr((1149, 128, 1237, 147)):
                if res[1] > 0.8:
                    if re_res := re.match(pattern, res[0].replace(" ", "").replace("：", ":")):
                        log.info(f"JYH end time: {res[0]}")
                        return re_res.group(0)

    def run(self):
        sleep(self.ui_delay)
        match_result = self.match_ui(self.uilist)
        log.insert("2.1", f"Matched UI: {match_result}")
        match match_result:
            case "jy_main_ui":
                if self.max_number == 0:
                    if not self.has_refreshed:
                        self.refresh_jy_list()
                        log.info(f"refresh_jy_list done")
                    elif self.left_max == 0 and self.right_max == 0:
                        self.find_max_number(same_server_seat)
                        self.find_max_number(diff_server_seat)
                    else:
                        log.info(f"left_max: {self.left_max}, right_max: {self.right_max}")
                        self.max_number = max(self.left_max, self.right_max)
                        self.finally_number = self.max_number
                else:
                    log.info(f"Max number: {self.max_number}, continue ")
                    if self.left_max > self.right_max:
                        log.info(f"left_max: {self.left_max} > right_max: {self.right_max}")
                        self.area_click(diff_server_seat[1], double_click=True, double_click_time=0.2)
                        sleep(0.5)
                        self.find_max_number(same_server_seat)
                    else:
                        log.info(f"left_max: {self.left_max} < right_max: {self.right_max}")
                        self.area_click(same_server_seat[1], double_click=True, double_click_time=0.2)
                        sleep(0.5)
                        self.find_max_number(diff_server_seat)
                log.info(f"Max number: {self.max_number}, continue ")

            case "yc_page":
                self.ward_yc()
            case "self_ward":
                if hasattr(self, "next_time"):
                    return
                sleep(1)
                self.area_click((614, 344, 625, 397))
