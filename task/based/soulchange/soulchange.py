from task.based.switchui.SwitchUI import SwitchUI
from task.based.Mytool.Click import Click
from task.based.Mytool.imageRec import ImageRec
from PIGEON.log import log
from task.based.soulchange.res.img_info_auto_create import *
from time import sleep


class SoulChange:
    def __init__(self, **kw):
        self.switchUI = SwitchUI(running=kw.get("running"))
        self.click = Click()
        self.imageRec = ImageRec()

        pass

    def changeSoulTo(self, soul: str):

        group = soul.split(",")[0]
        plan = soul.split(",")[-1]
        log.info(f"开始切换御魂: 组{group} ,方案{plan}")
        self.switchUI.switch_to("soul_content_page")
        sleep(1)  # 等待界面加载
        if self.imageRec.match_img(soul_content_ui):
            log.info("已在 soul 界面")
            self.click.area_click(soul_preinstall[1], animation_time=0.5)
            sleep(0.5)
            self.click.slide((1168, 172, 1202, 207), (1161, 466, 1193, 517), move_time=0.5)
            sleep(1.5)
            log.info("切换御魂方案")
            match group:
                case "1":
                    self.click.area_click(soul_group1[1], double_click=0.5)
                case "2":
                    self.click.area_click(soul_group2[1], double_click=0.5)
                case "3":
                    self.click.area_click(soul_group3[1], double_click=0.5)
                case "4":
                    self.click.area_click(soul_group4[1], double_click=0.5)
                case "5":
                    self.click.area_click(soul_group5[1], double_click=0.5)
                case "6":
                    self.click.area_click(soul_group6[1], double_click=0.5)
                case "7":
                    self.click.area_click(soul_group7[1], double_click=0.5)
                case _:
                    log.error("未知的 soul group")
            sleep(2)
            match plan:
                case "1":
                    self.click.area_click(soul_plan1[1], double_click=0.5)
                case "2":
                    self.click.area_click(soul_plan2[1], double_click=0.5)
                case "3":
                    self.click.area_click(soul_plan3[1], double_click=0.5)
                case _:
                    log.error("未知的 soul plan")
            sleep(1)
            for _ in range(5):
                if res := self.imageRec.match_img(change_confirm):
                    self.click.area_click(res)
                    sleep(1)
