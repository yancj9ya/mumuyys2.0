# 寄养的自动上卡

from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec
from tool.Mytool.Ocr import Ocr
from task.jysk.res.img_info_auto_create import *
from time import sleep
from PIGEON.log import log
from PIGEON.retry import retry
from tool.Mytool.Counter import Counter
from random import choices
from time import time
import re


class Jysk:
    def __init__(self, **kwargs):
        self.running = kwargs.get("STOPSIGNAL", None)
        self.click = Click()
        self.image_rec = ImageRec()
        self.ocr = Ocr()
        self.ui_delay = 0.5
        self.ui_list = [SK, WARD_MAIN]
        self.task_switch = True

    def run(self):
        """main logics of the program"""
        sleep(self.ui_delay)
        match_result = self.image_rec.match_ui(self.ui_list)
        log.insert("2.1", f"Matched UI: {match_result}")
        match match_result:
            case "SK":
                self.sk()
            case "WARD_MAIN":
                self.ward_main()
            case _:
                pass
        pass

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
        pass

    def set_parms(self, *args, **kwargs):
        """设置参数"""
        self.target_level = [int(i) for i in kwargs.get("target_level", "5,6").split(",")]
        self.target_count = [int(i) for i in kwargs.get("target_count", "8,9").split(",")]
        print(f"target_level: {self.target_level}, target_count: {self.target_count}")
        pass

    def ward_main(self):
        """寄养的自动上卡"""
        # 点击进入结界卡主界面
        self.click.area_click(ENTER_SK)

    def get_last_reward(self):
        """领取上次奖励"""
        if hasattr(self, "need_get_reward"):
            self.click.xclick()
            sleep(1)
            self.click.area_click(UN_END_BOX[1])
            sleep(1)
            self.click.area_click(ENTER_SK)
            sleep(1)

    def sk(self):
        """结界卡自动上卡"""
        # 先判断是否有卡
        if self.image_rec.match_img(FILL_CONFIRM, accuracy=0.8):
            # 获取剩余时间
            rest_time = self.get_rest_time()
            log.info(f"剩余时间: {rest_time}")
            self.need_get_reward = True
        else:
            rest_time = "00:00:00"

        # 判断是否需要上卡
        if rest_time == "00:00:00":  # 如果剩余时间为00:00:00，则需要上卡
            # 先领取奖励
            self.get_last_reward()
            # 自动上结界卡
            self.auto_fill_sk()
        else:  # 如果剩余时间不为00:00:00，则不需要上卡
            self.next_time = rest_time
            self.click.xclick()

    def auto_fill_sk(self):
        """自动上结界卡"""

        # 切换类型到太鼓or other
        self.switch_type()

        # 搜寻需要更换的结界卡
        self.search_replace_sk()

    def search_replace_sk(self):
        """搜索并更换结界卡"""
        # 循环搜索并更换结界卡
        while True:
            serch_area = self.image_rec.match_duo_img(SIX_GY)
            for rect in serch_area:
                level = self.get_star_level(rect)
                if level in self.target_level:
                    # 获取数量识别ocr区域
                    count_area = [rect[0] + 113, rect[1] - 8, rect[2] + 132, rect[3] + 8]
                    count_str = self.ocr.ocr_by_re(count_area, r"^勾玉\s*\+([7-9])/h$", threshold=0.8).group(1)
                    if int(count_str) in self.target_count:
                        # 点击结界卡
                        self.click.area_click(rect)
                        # 点击确认按钮
                        log.info(f"level: {level}, count: {count_str}")
                        self.click.area_click(ACTIVE_CARD)
                        sleep(2)
                        self.click.area_click(ACTIVE_CARD_CONFIRM)
                        return
                else:
                    continue

            self.list_down()

    def list_down(self):
        """下拉列表"""
        self.click.click(367, 235)
        self.click.mouse_scroll(("down", 6), 367, 235)
        sleep(0.2)

    def get_star_level(self, rect):
        """获取星级"""
        IMG_5STAR = [FIVE_GY[0], rect, FIVE_GY[2]]
        IMG_6STAR = [SIX_GY[0], rect, SIX_GY[2]]
        if self.image_rec.match_img_by_hist(IMG_5STAR, accuracy=0.8):
            return 5
        elif self.image_rec.match_img_by_hist(IMG_6STAR, accuracy=0.8):
            return 6
        else:
            return 0

    def get_rest_time(self):
        """获取剩余时间"""
        while True:
            pattern = r"^[0-2][0-9]:[0-5][0-9]:[0-5][0-9]$"
            rest_time = self.ocr.ocr_by_re(OCR_TIME_A, pattern, threshold=0.9, range_color=["aa3810", (30, 120, 150)], debug=True)
            if rest_time is not None:
                return rest_time.group()

    def switch_type(self):
        """切换卡池"""
        while True:
            # 先识别出卡池类型，再点击切换按钮
            type_str = self.ocr.ocr_by_re(OCR_TYPE_A, r"^太鼓|全部$", threshold=0.9).group()
            if type_str == "全部":
                self.click.area_click(OCR_TYPE_A)
                sleep(0.5)
                self.click.area_click([386, 251, 491, 289])  # 选择太鼓卡池
            elif type_str == "太鼓":
                return

        pass
