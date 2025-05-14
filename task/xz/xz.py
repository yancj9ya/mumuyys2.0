from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec

from task.xz.res.others_img_info import *
from task.xz.res.img_info_auto_create import *
from time import sleep, time, strftime, localtime
from PIGEON.log import log


class Xz:
    __instance = None
    __thread_instalce = None

    def __new__(cls):
        if Xz.__instance is None:
            Xz.__instance = object.__new__(cls)
        return Xz.__instance

    def __init__(self, **kwds):
        self.check_interval = 3
        self.running = None
        self.eye = ImageRec()
        self.hand = Click()
        self.count = 0
        self.thread_count = 0
        self.need_match_ui_list = [xz_yes, UNEXPECT_IMG_GHNPF, FULL_MSG_BOX]

    def __call__(self, **kwds):
        if self.__thread_instalce is None:
            # self.set_parms(**kwds)
            self.__thread_instalce = self
            self.loop()

        else:
            log.error("守护进程已启动")
            return
        pass

    def loop(self):
        print(f"协助邀请守护进程启动")
        while self.running.get():
            try:
                self.run()
                sleep(0.2)
            except Exception as e:
                log.error(f"协助邀请守护进程异常:{e}")
        else:
            print("协助邀请守护进程结束")
            return

    def new_sleep(self):
        if int(time()) % self.check_interval == 0:
            return True
        else:
            return False

    def run(self):
        # 延迟3秒
        self.sleep.wait(timeout=3)
        # 检测客户端是否启动
        if not self.dedect_client():
            # 客户端未启动
            print("客户端未启动")
            sleep(20)
            return
        # 客户端启动
        matched_UI = self.eye.match_ui(self.need_match_ui_list, accuracy=0.9)
        # print(f"匹配到的UI:{matched_UI}")
        match matched_UI:
            case "xz_yes":
                self.xz()
            case "UNEXPECT_IMG_GHNPF":
                self.GHNPF()
            case "FULL_MSG_BOX":
                self.full_of_card()
            case _:
                pass

    def full_of_card(self):
        log.info("结界卡溢出提醒：开始处理")
        # 检查是否勾选今日忽略
        if self.eye.match_img(CHECK_IGNORE_NOTION):
            log.info("结界卡溢出提醒：已勾选今日忽略")
            self.hand.area_click(CANCEL_NOTION)
        else:
            self.hand.area_click(CHECK_IGNORE_NOTION[1])
            sleep(0.5)

    def GHNPF(self):
        # 处理姑获鸟的皮肤活动弹窗
        log.info("检测到姑获鸟皮肤活动弹窗")
        return self.hand.area_click(UNEXPECT_IMG_GHNPF[1])

    def xz(self):
        # 是接受还是拒绝
        click_target = xz_yes[1]
        ####
        if self.eye.match_img(xz_yes):
            log.info("发现协助邀请")
            if self.eye.match_img(xz_no):
                log.info("确认协助邀请")
                self.hand.area_click(click_target)
                log.info("接受协助邀请")
                self.count += 1
            log.info(f"协助邀请守护进程结束,共接受邀请{self.count}次")
        pass

    def dedect_client(self):
        return self.eye.win.is_windows_exist()

    def set_parms(self, **kwargs):
        self.sleep = kwargs.get("event")
        self.running = kwargs.get("STOPSIGNAL", True)
        self.sleep.set()
        pass
