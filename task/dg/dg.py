from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec
from tool.Mytool.Ocr import Ocr
from tool.wxocr.wxocr import WxOcr
from tool.Mytool.Counter import Counter
from task.dg.res.img_info import *
from task.dg.res.img_info_auto_create import *
from time import sleep, time, strftime, localtime
from win11toast import toast
from PIGEON.log import Log
import traceback, random

log = Log()


class Dg(Click, ImageRec):
    def __init__(self, **kwargs):
        Click.__init__(self)
        ImageRec.__init__(self)
        self.ocr = WxOcr()
        self.uilist = [FINAL_FAIL, dg_ready_ui, dg_fail_ui, VICTORY, damo_ui, dg_fight_ui, dg_chose_ui]
        self.main_ui_sleep = 0.5
        self.DG_TIME = None
        self.DG_SWITCH = True
        self.counter = Counter()
        self.dg_rs = 70
        self.dg_xs = "2:5"
        self.running = kwargs.get("STOPSIGNAL", True)
        self.chdg_action = "GET_TARGET"
        self.target_list = []
        self._need_flush_target_list = False
        self._need_slide_target_list = False
        self._target_list_page = 1

    def decide_attack_or_not(self, dg_xs: float, dg_rs: int) -> bool:
        # 获取预设的系数和最小人数限制
        pre_rs = int(self.dg_rs)  # 确保预设的最小人数限制是整数
        pre_xs_min = float(self.dg_xs.split(":")[0])
        pre_xs_max = float(self.dg_xs.split(":")[1])
        # 获取在预设最小人数前提上根据系数的增量人数,如果系数小于4，则增量人数为0
        add_rs = int((dg_xs - 4.0) * 60) if dg_xs >= 4.0 and pre_rs >= 70 else 0  # and dg_rs >= 100
        # 判断系数是否在预设范围且人数符合条件，符合则返回True，否则返回False
        if all([pre_xs_min <= dg_xs <= pre_xs_max, pre_rs + add_rs <= dg_rs, dg_rs <= 150]):
            log.info(f"进攻道馆：系数{dg_xs:.2f}，人数{dg_rs},赏金{self.target_fund}万，符合要求")
            return True
        else:
            return False
        pass

    def dg_end(self):
        c = 0
        if self.dg_ticket > 0:
            log.info(f"道馆进攻结束,wait for 60s")
            self.counter.add_record("last")
            self.counter.reset()
            while self.running.is_set():
                c += 1
                if c > 40:
                    break
                sleep(1.5)
        elif self.dg_ticket == 0:
            sleep(2)
            if self.match_img(FINAL_FAIL):
                self.area_click(FINAL_FAIL[1])
            self.xclick()
            sleep(1)
            self.area_click(EXIT_CONFIRM)
            self.DG_SWITCH = False

            log.insert("4.0", f"道馆结束，共进攻：{self.counter.get_record('last')}+{self.counter.count}={self.counter.count+self.counter.get_record('last')  if self.counter.get_record('last') else self.counter.count}次")

    def _is_dg_build(self):
        if not self.match_color_img_by_hist(DG_BUILDED):
            log.warning("道馆未建立")
            toast(f"道馆未建立，手动建立道馆", scenario="incomingCall", button="已建立，继续")

        return

    def get_dg_ticket(self):
        """获取道馆进攻的次数"""
        try:
            match = self.ocr.ocr_by_re([499, 625, 705, 671], "([0-2])次", threshold=0.8, debug=False)
            if match:
                return int(match.group(1))
        except Exception as e:
            log.error(f"get_dg_ticket()函数出错了：{e}，traceback:{traceback.format_exc()}")
            return None

    # 重写一下dg_chose函数
    def dg_chose_2(self):
        """
        选择道馆进攻的页面主要有4个层面的逻辑
        1.判断进攻结界的次数是否为0，如果为0，则退出
        2.识别右侧的结界列表中的道馆赏金，并点击使目标道馆的信息页面划出，并且每识别一次页面需要向下滑动列表，每滑动三次需要刷新列表
        3.当目标道馆的信息卡片划出后识别目标道馆的人数，并计算出系数；添加：识别出高于见习的结界数量，计算出这部分的占比，用作判断是否进攻的条件
        4.判断是否符合进攻条件，符合则点击左侧的进攻按钮，并开始挑战

        因此在此页面需要有多种操作符，按照操作符来进行执行实际对应的动作
        操作符包括：「GET_TARGET GET_CARD_INFO 」
        """
        # 利用重试机制判断进攻次数是否为0
        try:
            if self.dg_ticket == 0:
                log.info("道馆可进攻次数为0，退出")
                self.DG_SWITCH = False
                return
        except Exception as e:
            # 首次抛出异常，获取次数
            ocr_dg_ticket = self.get_dg_ticket()
            if ocr_dg_ticket != None:
                self.dg_ticket = ocr_dg_ticket
                log.info(f"道馆可进攻次数：{self.dg_ticket}")
                log.insert("3.1", f"道馆可进攻次数：{self.dg_ticket}")
                # 顺便判断一下道馆是否建立
                self._is_dg_build()
            # todo
            return

        match self.chdg_action:
            case "GET_TARGET":
                self.get_target()
            case "GET_CARD_INFO":
                self.get_card_info()
            case _:
                pass

    def flush_list(self):
        """刷新右侧道馆列表"""
        if self._target_list_page == 3 and self._need_flush_target_list:
            # todo: 改用图像识别保证刷新成功
            self.area_click([1129, 613, 1193, 678])
            sleep(1)
            self.area_click([686, 403, 796, 443])
            sleep(1)
            self._target_list_page = 1
            self._need_flush_target_list = False
            log.info("list flushed")

    def slide_list(self):
        """向下滑动道馆列表"""
        if self._target_list_page < 3 and self._need_slide_target_list:
            self.mouse_scroll(("down", 9), 1158, 310)
            sleep(0.5)  # 等待滚动完成
            log.info("list slided")
            self._target_list_page += 1
            self._need_slide_target_list = False

    def get_target(self):
        """获取右侧目标道馆的信息"""

        # 首先判断self.target_list是否为空
        if not self.target_list:
            # 图像为空则有三个对应的选项，分别是：
            # 1. 刷新列表
            # 2. 向下滑动列表
            # 3. 识别出右侧道馆目标的赏金图片的位置，返回值是一个列表，列表中有多个坐标位置
            if self._need_flush_target_list:
                self.flush_list()
            elif self._need_slide_target_list:
                self.slide_list()
            else:
                self.target_list = self.match_duo_img(dg_coin_right_ui, accuracy=0.8, debug=False)[::-1]  # 反向
                print(f"{len(self.target_list)=}")
        else:
            # 取出一个坐标位置，并点击使目标道馆的信息页面划出
            target_coord = self.target_list.pop()
            # 如果弹出后target_list为空，则需要判断是滑动还是刷新列表
            if not self.target_list:
                if self._target_list_page == 3:
                    self._need_flush_target_list = True
                else:
                    self._need_slide_target_list = True
            # 识别出赏金
            ocr_area = [target_coord[0] + 25, target_coord[1], target_coord[2] + 73, target_coord[3]]
            match = self.ocr.ocr_by_re(ocr_area, "([0-9]{3})万", threshold=0.7, pre_hand={"binary": False, "enlarge": 5})
            if match:
                self.target_fund = int(match.group(1))
                # 点击赏金位置
                self.area_click(ocr_area)
                # 切换action
                self.chdg_action = "GET_CARD_INFO"
            else:
                # 识别失败，重新加入列表还是跳过呢？
                pass  # 先跳过

    def get_card_info(self):
        """获取目标道馆的信息卡片,并根据数据判断是否进攻该目标"""

        # 定义一个判断是否动画结束的函数，坐标的目标道馆滑动动画
        def is_end_ani():
            # 先识别一次
            fir_res = self.match_img(dg_chose_left_ui)
            # 等待0.1s，再次识别，判断识别区域的位置是否变化
            sleep(0.1)
            sec_res = self.match_img(dg_chose_left_ui)
            # 两次识别结果是否一致
            return fir_res if fir_res == sec_res else None

        try:
            # 识别出目标道馆的人数
            if anchor_card := is_end_ani():  # 取得左边的道馆人数ui位置
                anchor_card_ocr_rs_area = [
                    anchor_card[0] + 225,
                    anchor_card[1] + 35,
                    anchor_card[0] + 280,
                    anchor_card[1] + 65,
                ]
                match = self.ocr.ocr_by_re(anchor_card_ocr_rs_area, "([1]?[0-9]{2})人", threshold=0.7, pre_hand={"binary": False, "enlarge": 5})
                if match:
                    self.target_rs = int(match.group(1))
                    # print(f"{self.target_fund=} {self.target_rs=} {self.target_fund/self.target_rs=:.2f}")
                    # 计算系数
                    self.target_xs = (self.target_fund / self.target_rs) if self.target_rs != 0 else 10  # 计算系数
                    log.info(f"目标系数：{self.target_xs:.2f}，{self.target_fund}万，{self.target_rs}人")
                    # 判断是否符合进攻条件
                    attact_or_not = self.decide_attack_or_not(self.target_xs, self.target_rs)
                    if attact_or_not:
                        log.insert("5.1", f"目标道馆：{self.target_fund}万，{self.target_rs}人，系数：{self.target_xs:.2f}")
                        self.area_click(
                            [
                                anchor_card[0] + 312,
                                anchor_card[1] + 92,
                                anchor_card[0] + 312 + 33,
                                anchor_card[1] + 92 + 35,
                            ]
                        )
                        sleep(2)
                        self.area_click([705, 409, 815, 447])  # 确定挑战
                        sleep(2)
                        self.DG_TIME = None
                self.chdg_action = "GET_TARGET"
            else:
                # 识别失败，可能是因为动画未结束
                pass

        except Exception as e:
            log.error(f"get_card_info()函数出错了：{e}，traceback:{traceback.format_exc()}")
        finally:
            # 切换action
            # self.chdg_action = "GET_TARGET"
            pass

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
        self.dg_ticket -= 1
        log.insert("3.0", f"开始进攻，剩余次数：{self.dg_ticket}")
        # 重置参数
        self._need_flush_target_list = False
        self._need_slide_target_list = False
        self.target_list = []
        self.chdg_action = "GET_TARGET"

        self.dg_end()
        sleep(1)

        pass

    def dg_ready_ui(self):
        if not self.DG_TIME:
            log.insert("4.1", f"wait for start ...")
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
            if self.match_img(img, accuracy=0.8, needMask=dg_sign_mask):  # str(dg_sign_mask)
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
            self.counter.increment(interval=4)
            log.insert("4.0", f"正在第{[f'{self.counter.get_record('last')}+' if self.counter.get_record('last')  else ''][0]}{self.counter.count}次进攻道馆")
            sleep(1)

            if not self.img_dgsign(dg_sign):
                log.info(">>>未在准备后识别标记")
                if self.match_img(dg_btn_ready) == None:
                    log.info(">>>开始执行dgsign()")
                    self.dgsign()  # 如果没识别到标记，则执行标记函数
                return
        pass

    def _save_award_img(self):
        sleep(1)
        self.win.screenshot([218, 132, 1233, 617], save_img=True)
        log.info("结算界面：已经截图,返回准备界面")
        sleep(0.5)
        self.area_click([990, 462, 1125, 520])

        return

    def run(self):
        sleep(self.main_ui_sleep)
        match_result = self.match_ui(self.uilist)
        log.insert("2.1", f"Matched UI:{match_result}")
        match match_result:

            case "FINAL_FAIL":
                self.area_click(FINAL_FAIL[1])
            case "ready_ui":
                self.dg_ready_ui()
            case "fight_ui":
                self.dg_fight_ui()
            case "chose_ui":
                self.dg_chose_2()
            case "VICTORY":
                self.area_click(VICTORY[1])
            case "damo_ui" | "dg_fail_ui":
                self._save_award_img()
            case _:
                pass
        pass

    def loop(self):
        # log.clear()
        log.info(f"{'道馆进攻程序开始':*^22}")
        while self.DG_SWITCH:
            match self.running.state:
                case "RUNNING":
                    self.run()
                case "STOP":
                    return
                case "WAIT":
                    log.info("等待中...")
                    sleep(1)
                    continue
                case _:
                    pass

    def set_parms(self, **kwargs):

        self.main_ui_sleep = kwargs.get("main_ui_sleep", 0.5)
        self.dg_rs = int(kwargs.get("dg_rs", 70))
        self.dg_xs = kwargs.get("dg_xs", "2:5")
        log.insert("5.0", f"set 人数:{self.dg_rs},系数:{self.dg_xs} ")
