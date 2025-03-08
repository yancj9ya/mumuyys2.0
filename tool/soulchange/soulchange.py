from page.page_switch import nav
from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec
from PIGEON.log import log
from tool.soulchange.res.img_info_auto_create import *
from tool.Mytool.Ocr import Ocr
from time import sleep


class SoulChange:
    def __init__(self, **kw):
        self.switchUI = nav
        self.ocr = Ocr()
        self.click = Click()
        self.imageRec = ImageRec()
        self.GROUP_LIST = [GROUP1, GROUP2, GROUP3, GROUP4, GROUP5, GROUP6, GROUP7]
        self.GROUP_BTN = [soul_group1, soul_group2, soul_group3, soul_group4, soul_group5, soul_group6, soul_group7]
        self.PLAN_BTN = [soul_plan1, soul_plan2, soul_plan3]
        self.CHANGE_SUCCESS = False

    def confirm_page(self):
        """确认在御魂更换（式神录）的界面，防止出错"""
        print("confirm_page")
        _try_times = 3
        while not self.imageRec.match_img(SIKI_CONTENT):
            match self.task_switch.state:
                case "STOP":
                    log.info("已停止御魂更换")
                    return False
                case "WAIT":
                    log.info("暂停御魂更换")
                    continue
                case _:
                    pass
            try:
                self.switchUI.switch_to("SHIKI_RECORD", self.task_switch)
            except Exception as e:
                log.error(f"切换到式神录失败: {e}")
                continue

            print(f"confirm_page: {_try_times}")
            _try_times -= 1
            if _try_times == 0:
                log.error(f"无法跳转到式神录更换御魂 {_try_times}and{self.task_switch.state}")
                break
        else:
            log.info("已在御魂更换界面")

        pass

    def confirm_preset(self):
        """确认预设正常展开"""
        print("confirm_preset")
        while not self.imageRec.match_img(TEAM_PRESET):
            match self.task_switch.state:
                case "STOP":
                    log.info("已停止御魂更换")
                    return False
                case "WAIT":
                    log.info("暂停御魂更换")
                    continue
                case _:
                    pass
            self.click.area_click(soul_preinstall, animation_time=0.5)
        else:
            log.info("已确认预设正常展开,滑动到顶部")
            sleep(0.5)
            self.click.slide((1168, 172, 1202, 207), (1161, 466, 1193, 517), move_time=0.3)
            sleep(0.5)
        pass

    def confirm_group(self, group: str):
        """确认目标分组被点击选中"""
        match_area = self.GROUP_LIST[int(group) - 1]
        CHECKED[1] = match_area
        while not self.imageRec.match_color_img_by_hist(CHECKED):
            match self.task_switch.state:
                case "STOP":
                    log.info("已停止御魂更换")
                    return False
                case "WAIT":
                    log.info("暂停御魂更换")
                    continue
                case _:
                    pass
            self.click.area_click(self.GROUP_BTN[int(group) - 1], animation_time=0.05)
            sleep(0.5)
        else:
            log.info(f"已确认分组{group}被选中")
        pass
        pass

    def check_substring(self, main_string, substring_list):
        for substring in substring_list:
            if substring in main_string:
                return True
        return False

    def confirm_plan(self, plan: str):
        """确认目标御魂方案被更换成功"""
        SUB_STR = ["契灵成功", "使用预设御魂", "装备御魂成功"]
        match_area = self.PLAN_BTN[int(plan) - 1]
        while True:
            match self.task_switch.state:
                case "STOP":
                    log.info("已停止御魂更换")
                    return False
                case "WAIT":
                    log.info("暂停御魂更换")
                    continue
                case _:
                    pass
            self.click.area_click(match_area, animation_time=0.05)
            sleep(0.5)
            res = self.ocr.ocr((520, 228, 769, 260))
            print(res)
            if res[1] > 0.8 and self.check_substring(res[0], SUB_STR):
                log.info(f"已更换御魂方案{plan}")
                self.CHANGE_SUCCESS = True
                break
            else:
                self.confirm_change()
            sleep(1)
        pass

    def confirm_change(self):
        """御魂更换时弹出的其他式神已佩戴提示确定"""
        if self.imageRec.match_img(change_confirm):
            self.click.area_click(change_confirm[1])
        pass

    def confirm_soulpet_change(self):
        """御魂更换时弹出的契灵已佩戴提示确定"""
        pass

    def parse_plan_str(self, plan_str: str):
        """解析御魂方案字符串"""
        plan_str = plan_str.strip().replace(".", ",")
        group = plan_str.split(",")[0]
        plan = plan_str.split(",")[-1]
        return group, plan

    def changeSoulTo(self, soul: str, task_switch):
        """更换御魂"""
        self.CHANGE_SUCCESS = False
        self.task_switch = task_switch
        try:
            print(f"开始更换御魂: {soul}")
            # 解析御魂分组方案信息
            group, plan = self.parse_plan_str(soul)
            log.info(f"开始切换御魂: <组{group} ,方案{plan}>")
            while not self.CHANGE_SUCCESS:
                match self.task_switch.state:
                    case "STOP":
                        log.info("已停止御魂更换")
                        return False
                    case "WAIT":
                        log.info("暂停御魂更换")
                        continue
                    case _:
                        pass
                # 切换到御魂更换界面
                self.confirm_page()

                # 确认预设正常展开
                self.confirm_preset()

                # 确认目标分组被点击选中
                self.confirm_group(group)

                # 确认目标御魂方案被更换成功
                self.confirm_plan(plan)
            else:
                log.info(f"御魂更换成功: 组{group} ,方案{plan}")
                # if self.imageRec.match_img(BACK_BTN):
                #     self.click.area_click(BACK_BTN[1])
                self.click.xclick()
                sleep(1)
                return True
        except Exception as e:
            log.error(f"御魂更换失败: {e}")
