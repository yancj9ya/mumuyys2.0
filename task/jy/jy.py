from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec
from tool.Mytool.Ocr import Ocr
from task.jy.res.img_info_auto_create import *
from time import sleep
from PIGEON.log import log
from PIGEON.retry import retry
from tool.Mytool.Counter import Counter
from random import choices
from time import time
import re


class Jy(Click, ImageRec):
    def __init__(self, **kwargs):
        Click.__init__(self)
        ImageRec.__init__(self)
        self.running = kwargs.get("STOPSIGNAL", None)
        self.task_switch = True
        self.ui_delay = 0.5
        self.ocr = Ocr()
        self.uilist = [jy_main_ui, yc_page, self_ward]
        self.has_refreshed = False
        self.max_number = 0
        self.left_max = 0
        self.right_max = 0

    def loop(self):
        """main loop of the program"""

        while self.task_switch:
            match self.running.state:
                case "RUNNING":
                    if hasattr(self, "next_time"):
                        self.task_switch = False
                        continue
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

    def set_parms(self, *args, **kwargs):
        """set parameters for the program"""
        # 优先级设置
        default_priority_list = "151,143,79,128,67,59"
        self.priority_list: str = kwargs.get("priority", default_priority_list)
        self.priority = {int(value): index for index, value in enumerate(self.priority_list.split(","))}
        # 设置类型
        self.target_type = kwargs.get("target_type", "BOTH")

        # 根据类型设置搜索的目标图像列表
        match self.target_type:
            case "TG":
                self.target_img_list = [six_star_img, five_star_img]
                self.key_wd = "勾玉"
            case "DY":
                self.target_img_list = [six_dy_img, five_dy_img]
                self.key_wd = "体力"
            case "BOTH":
                self.target_img_list = [six_star_img, five_star_img, six_dy_img, five_dy_img]
                self.key_wd = ["勾玉", "体力"]

        log.insert("3.0", f"target_type: {self.key_wd}")
        log.insert("4.0", f"priority_list: {self.priority_list}")

        pass

    @retry(max_retries=3, delay=1, exceptions=(Exception,))
    def get_right_jj_num(self):
        """get current JJ number from the right place"""
        ocr_res = self.ocr.ocr((795, 425, 977, 453))
        log.info(f"OCR result: {ocr_res[0]}")

        # 处理点击过快，导致太鼓变成斗鱼或其他的情况
        # 判断左边文字的类型是否符合目标
        match self.target_type:
            case "TG":
                if self.key_wd not in ocr_res[0]:
                    return 0
            case "DY":
                if self.key_wd not in ocr_res[0]:
                    return 0
            case "BOTH":
                if all(key_text not in ocr_res[0] for key_text in self.key_wd):
                    return 0

        # 如果OCR识别的置信度符合条件
        if ocr_res[1] > 0.6:

            # 清除字符串中的非数字部分，提取出结界卡的数量
            hand_res_str = re.sub(r"[^0-9]", "", ocr_res[0])

            # 如果结界卡是目标值，则返回结界卡数量
            if int(hand_res_str) in self.priority.keys():
                return int(hand_res_str)
            else:
                print(f"OCR number not in target pool: {hand_res_str=} {self.priority=} {self.priority.keys()=}")
        else:
            raise Exception("Failed to get right JJ number")

    def scroll_down(self):
        """scroll down to bottom of the screen"""
        self.area_click([439, 207, 503, 238])
        self.mouse_scroll(("down", 6), 460, 224)
        sleep(0.2)
        pass

    def get_target_pos(self):
        """get the position of target area"""
        # 返回的识别区域列表
        rec_list = []
        # 对每张图片进行识别
        for target_img in self.target_img_list:
            if rec_img_list := self.match_duo_img(target_img, 0.8):
                rec_list.extend(rec_img_list)
        return rec_list

    def custom_max(self, a, b):
        """
        param a: int
        param b: int
        reture int
        比较两个数按照给定的优先级，返回较大的那个数，如果优先级相同则返回b
        """
        # 数据检查
        assert a in self.priority and b in self.priority, "error number not in priority list"

        # 处理为0的情形
        if a == 0:
            return b
        if b == 0:
            return a

        return a if self.priority[a] < self.priority[b] else b

    def re_serch(self):
        """get the max number of same and diff server JY list"""
        sleep(1)
        temp_re_num = 0
        rec_list = self.get_target_pos()
        try:
            for area in rec_list:
                log.info(f"found {len(rec_list)} target in this page")
                self.area_click(area)
                sleep(1)
                temp_num = self.get_right_jj_num()
                print(f"{temp_num=}")
                if temp_num:
                    if temp_num == max(self.priority.keys()) or (hasattr(self, "finally_number") and temp_num == self.finally_number):
                        self.get_in_to_jy()
                        self.finally_number = temp_num
                        self.next_time = "06:00:00"
                        return "success"
                    temp_re_num = self.custom_max(temp_re_num, temp_num)
                    log.info(f"Found JJ number: {temp_num}")
            return temp_re_num
        except Exception as e:
            log.error(f"Error in re_serch: {e}")
            return None
        finally:
            # self.slide((517, 580), (557, 200), move_time=1)
            self.scroll_down()

    def refresh_jy_list(self):
        """flash list of same and diff server by slide to bottom"""
        log.info("Refreshing JY list...")
        if not self.has_refreshed:
            sleep(0.5)
            self.slide((190, 191), (195, 560), move_time=1)  # 下拉刷新同区好友
            sleep(0.5)
            self.area_click(diff_server_seat[1])
            sleep(1)
            self.slide((190, 191), (195, 560), move_time=1)  # 下拉刷新跨区好友
            self.area_click(same_server_seat[1])
            sleep(0.5)
            self.has_refreshed = True
        else:
            log.info("Already refreshed")
        sleep(0.5)

    def find_max_number(self, area_type):
        """Find the max number from a given area (left or right)."""
        if hasattr(self, "next_time"):
            return  # 如果已经设置了下一次运行时间说明已经蹲了结界，则不再继续查找
        self.area_click(area_type[1], double_click=True, double_click_time=0.2)
        sleep(0.2)
        log.info(f"Finding max number in {area_type[-1]}...\n left_max: {self.left_max}, right_max: {self.right_max}")
        for _ in range(5):
            if serch_max_num := self.re_serch():
                if isinstance(serch_max_num, int):
                    if area_type == same_server_seat:
                        self.left_max = self.custom_max(self.left_max, serch_max_num)
                    else:
                        self.right_max = self.custom_max(self.right_max, serch_max_num)
        sleep(0.5)

    def get_in_to_jy(self):
        """enter cofirmed ward and excute then return to self ward"""
        confirm_jy_success = False
        while not confirm_jy_success:
            sleep(0.5)
            if self.match_img(enter_jy):
                self.area_click(enter_jy[1])
                log.info("Enter JY page")
            if self.match_img(jy_sure_page):
                # todo:检查是否有空位寄养
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

            # 任务控制退出
            if self.running.state == "STOP":
                return

        while True:
            # 任务控制退出
            if self.running.state == "STOP":
                return
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
        """confirm jy or not if yes then set self.next_time -> self.next_time"""
        res = self.match_img(blank_seat_2)
        log.info(f"Blank seat 2: {res}")
        if res:
            self.area_click(blank_seat_2[1])
            sleep(0.5)
        else:
            self.next_time = self.get_jyh_end_time()
            self.area_click(exit_jy_page[1])

    def get_jyh_end_time(self):
        """get the end time of JY"""
        pattern = r"^[0][0-5]:[0-5][0-9]:[0-5][0-9]$"
        while True:
            sleep(1)
            if res := self.ocr.ocr_by_re((1149, 128, 1237, 147), pattern=pattern, range_color=["c0baa9", (10, 10, 50)]):
                log.info(f"JYH end time: {res.group()}")
                return res.group()

    def run(self):
        """main logics of the program"""
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
                        return
                    else:
                        log.info(f"left_max: {self.left_max}, right_max: {self.right_max}")
                        self.max_number = self.custom_max(self.left_max, self.right_max)
                        self.finally_number = self.max_number
                else:
                    log.info(f"Max number: {self.max_number}, continue ")
                    if self.custom_max(self.left_max, self.right_max) == self.right_max:
                        log.info(f"left_max < right_max , go to diff server")
                        self.area_click(diff_server_seat[1], double_click=True, double_click_time=0.2)
                        sleep(0.5)
                        self.find_max_number(diff_server_seat)
                    else:
                        log.info(f"left_max > right_max , go to same server")
                        self.area_click(same_server_seat[1], double_click=True, double_click_time=0.2)
                        sleep(0.5)
                        self.find_max_number(same_server_seat)
                log.info(f"Max number: {self.max_number}, continue ")

            case "yc_page":
                self.ward_yc()
            case "self_ward":
                if hasattr(self, "next_time"):
                    return
                sleep(1)
                self.area_click((614, 344, 625, 397))
