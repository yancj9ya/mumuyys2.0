from task.based.Mytool.Click import Click
from task.based.Mytool.imageRec import ImageRec
from task.based.Mytool.Ocr import Ocr
from task.based.Mytool.Counter import Counter
from task.dg.res.img_info import *
from time import sleep, time, strftime, localtime

from PIGEON.log import Log
import traceback

log = Log()


class Dg(Click, ImageRec):
    def __init__(self, **kwargs):
        Click.__init__(self)
        ImageRec.__init__(self)
        self.uilist = [dg_ready_ui, dg_fight_ui, dg_chose_ui]
        self.main_ui_sleep = 0.5
        self.DG_TIME = None
        self.DG_SWITCH = True
        self.DG_COUNT = 1
        self.counter = Counter()
        self.dg_rs = 70
        self.dg_xs = "2:5"
        self.running = kwargs.get("STOPSIGNAL", True)

    def decide_attack_or_not(self, dg_xs: float, dg_rs: int) -> bool:
        # 获取预设的系数和最小人数限制
        pre_rs = int(self.dg_rs)  # 确保预设的最小人数限制是整数
        pre_xs_min = float(self.dg_xs.split(":")[0])
        pre_xs_max = float(self.dg_xs.split(":")[1])
        # 获取在预设最小人数前提上根据系数的增量人数,如果系数小于4，则增量人数为0
        add_rs = int((dg_xs - 4.0) * 60) if dg_xs >= 4.0 else 0  # and dg_rs >= 100
        # 判断系数是否在预设范围且人数符合条件，符合则返回True，否则返回False
        if all([pre_xs_min <= dg_xs <= pre_xs_max, pre_rs + add_rs <= dg_rs, dg_rs <= 150]):
            log.insert("3.0", f"进攻道馆：系数{dg_xs:.2f}，人数{dg_rs}")
            return True
        else:
            return False
        pass

    def dg_end(self):
        c = 0
        if self.DG_COUNT > 0:
            log.info(f"道馆进攻结束,wait for 60s")
            self.counter.add_record("last")
            self.counter.reset()
            while self.running.is_set():
                c += 1
                if c > 40:
                    break
                sleep(1.5)
        elif self.DG_COUNT == 0:
            self.DG_SWITCH = False
            log.insert("4.0", f"道馆结束，共进攻：{self.counter.get_record('last')}+{self.counter.count}={self.counter.count+self.counter.get_record('last')  if self.counter.get_record('last') else self.counter.count}次")

    def chose_dg(self):
        try:
            if res := Ocr.ocr([499, 625, 705, 671]):
                res = list(res)
                res[0] = res[0].strip()
                # log.info(f'{res}')
                if res[1] > 0.8:
                    numbers = 1 if "".join(filter(str.isdigit, res[0])) == "" else int("".join(filter(str.isdigit, res[0])))
                    if numbers == 0:
                        self.DG_SWITCH = False
                    else:
                        self.DG_COUNT = numbers
                else:
                    # log.info(f'res[1]={res[1]}')
                    return
            else:
                return
            log.info(f"道馆可进攻次数：{self.DG_COUNT}")
            log.info(f"道馆SWITCH：{self.DG_SWITCH}")
            # while self.DG_SWITCH and not self.running.is_set():
            for i in range(3):
                if not self.running.is_set():
                    return
                if res := self.match_duo_img(dg_coin_right_ui, accuracy=0.8):
                    for area in res:
                        sleep(0.2)
                        if not self.running.is_set():
                            return
                        ocr_area = [area[0] + 35, area[1], area[2] + 43, area[3]]
                        ocr_result = Ocr.ocr(ocr_area)
                        if not ocr_result:
                            continue
                        dg_sj = ocr_result[0]  # 这个是返回道馆的赏金字符串
                        dg_sj_num = int("".join([char for char in dg_sj if char.isdigit()]))  # 采用列表推导式过滤出数字
                        self.area_click(ocr_area)
                        sleep(1.2)
                        left_area = self.match_img(dg_chose_left_ui)  # 取得左边的道馆人数ui位置
                        if not left_area:
                            continue
                        left_ocr_area = [
                            left_area[0] + 200,
                            left_area[1] + 40,
                            left_area[0] + 292,
                            left_area[1] + 60,
                        ]  # 根据左边的道馆ui，取得ocr识别的人数区域
                        dg_rs_result = Ocr.ocr(left_ocr_area)
                        if not dg_rs_result:
                            continue
                        dg_rs = int("".join([char for char in dg_rs_result[0] if char.isdigit()]))  # 改为列表推导式取出数字
                        dg_xs = (dg_sj_num / dg_rs) if dg_rs != 0 else 10  # 计算系数
                        log.info(f"{str(dg_sj_num):<3}万，{str(dg_rs):>4}人，系数：{dg_xs:.2f}")
                        if self.decide_attack_or_not(dg_xs, dg_rs):
                            log.insert("5.1", f"系数{dg_xs:.2f}，人数{dg_rs}符合要求，开始挑战")
                            self.area_click(
                                [
                                    left_area[0] + 312,
                                    left_area[1] + 92,
                                    left_area[0] + 312 + 33,
                                    left_area[1] + 92 + 35,
                                ]
                            )
                            sleep(2)
                            self.area_click([705, 409, 815, 447])  # 确定挑战
                            sleep(2)

                            self.DG_TIME = None
                            return
                self.mouse_scroll(("down", 9), 1158, 310)
            log.info("未能找到合适的系数道馆，刷新重找")
            self.area_click([1129, 613, 1193, 678])
            sleep(1)
            self.area_click([686, 403, 796, 443])
            sleep(1)
        except Exception as e:
            log.error(f"chose_dg()函数出错了：{e}，traceback:{traceback.format_exc()}")

    def giveup(self):
        log.info(f"放弃馆主,该次共进攻次数：{self.counter.count}")
        sleep(3)
        self.area_click([63, 607, 124, 673])  # 放弃突破按钮
        sleep(1)
        self.area_click([685, 401, 788, 442])
        sleep(0.3)
        for i in range(5):
            sleep(1)
            if self.match_img(dg_zaiz_ui):
                self.area_click(dg_zaiz_ui[1])
        self.DG_COUNT -= 1
        self.dg_end()
        sleep(1)

        pass

    def dg_ready_ui(self):
        if not self.DG_TIME:
            log.insert("4.1", f"wait for start {'.'*(int(time())%5)}")
            sleep(0.5)
        elif self.match_img(dg_end_ui):
            sleep(1)
            self.giveup()
        elif time() - self.DG_TIME < 1200:
            sleep(0.5)
            # todo: 增加判断是挑战按钮还是观战按钮
            if self.match_img(tiaozhan):
                self.area_click([1128, 562, 1228, 623])
                log.info(">>>开始挑战again")
                sleep(2)  # 等待动画
        else:
            sleep(1)
        pass

    def img_dgsign(self, img, times=5):
        for i in range(times):
            if self.match_img(img, accuracy=0.8):
                return True
            sleep(0.1)
        return False

    def dgsign(self):
        if self.match_img(fight_ui):
            log.info(">>>战斗已开始，开始标记")
            self.click(612, 560)  # 先标记神乐
            sleep(0.8)
            self.click(240, 489)  # 再标记输出防止意外取消标记
            log.info(">>>标记完成")

        pass

    def dg_fight_ui(self):
        if self.DG_TIME == None:
            self.DG_TIME = time()
            # 是否重置进攻次数计数器

            log.insert("2.1", strftime(" Start_TIME:%H:%M:%S", localtime(self.DG_TIME)))
            sleep(2)

        if self.match_img(dg_btn_ready):
            # sleep(0.5)
            self.area_click([1142, 553, 1221, 618], double_click=True)  # 点击准备按钮
            self.counter.increment()
            log.insert("4.1", f" * 正在第{[f'{self.counter.get_record('last')}+' if self.counter.get_record('last')  else ''][0]}{self.counter.count}次进攻道馆*")
            sleep(1)

            if not self.img_dgsign(dg_sign):
                log.info(">>>未在准备后识别标记")
                if self.match_img(dg_btn_ready) == None:
                    log.info(">>>开始执行dgsign()")
                    self.dgsign()  # 如果没识别到标记，则执行标记函数
                return
        elif self.match_img(damo_ui):
            sleep(1)
            self.screenshot(self.child_handle, [218, 132, 1233, 617], save_img=True)
            log.info("结算界面：已经截图,返回准备界面")
            sleep(0.5)
            self.area_click([990, 462, 1125, 520])
            return
        elif self.match_img(sl_ui):
            sleep(0.5)
            self.area_click([990, 462, 1125, 520])
            return
        elif self.match_img(dg_fail_ui) != None:  # 战斗失败，返回准备界面
            sleep(2)
            self.screenshot(self.child_handle, [218, 132, 1233, 617], save_img=True)
            log.info("进攻失败，返回准备界面")
            sleep(0.5)
            self.area_click([990, 462, 1125, 520])
            return
        pass

    def run(self):
        sleep(self.main_ui_sleep)
        match_result = self.match_ui(self.uilist)
        log.insert("2.1", f"Matched UI:{match_result}")
        match match_result:
            case "ready_ui":
                self.dg_ready_ui()
            case "fight_ui":
                self.dg_fight_ui()
            case "chose_ui":
                self.chose_dg()
            case _:
                pass
        pass

    def loop(self):
        # log.clear()
        log.info(f"{"道馆进攻程序开始":^27}")
        while self.DG_SWITCH:
            if not self.running.is_set():
                break
            self.run()

    def set_parms(self, **kwargs):

        self.main_ui_sleep = kwargs.get("main_ui_sleep", 0.5)
        self.dg_rs = int(kwargs.get("dg_rs", 70))
        self.dg_xs = kwargs.get("dg_xs", "2:5")
        log.info(f"set dg_rs:{self.dg_rs},dg_xs:{self.dg_xs}")
