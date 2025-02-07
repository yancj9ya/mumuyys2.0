from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec

from task.xz.res.others_img_info import *
from time import sleep, time, strftime, localtime
from PIGEON.log import log


class Xz:
    running = None
    eye = ImageRec()
    hand = Click()
    count = 0
    thread_count = 0

    @classmethod
    def dedect_client(cls):
        return cls.eye.win.is_windows_exist()

    @classmethod
    def auto_accept_mission(cls, **kwargs):
        try:
            # log.info("协助邀请守护进程启动")
            while cls.running.get():
                sleep(3)  # 每三秒检测一次是否有邀请
                # 检测客户端是否启动
                if not cls.dedect_client():
                    # 客户端未启动
                    sleep(20)
                    continue
                # 客户端启动
                if res := cls.eye.match_img(xz_yes):
                    log.info("发现协助邀请")
                    if cls.eye.match_img(xz_no):
                        log.info("确认协助邀请")
                        cls.hand.area_click(res)
                        log.info("接受协助邀请")
                        cls.count += 1
            log.info(f"协助邀请守护进程结束,共接受邀请{cls.count}次")
            cls.count = 0
            cls.thread_count -= 1

        except Exception as e:
            log.error(f"协助邀请守护进程异常:{e}")

    @classmethod
    def cooperation_mission_start(cls, **kwargs):
        if cls.thread_count != 0:
            log.info(f"{cls.thread_count}个,协助邀请守护进程已启动")
            return
        else:
            cls.thread_count += 1
            cls.running = kwargs.get("STOPSIGNAL", True)
            log.info(f"协助邀请守护进程启动 {cls.thread_count}")
            cls.auto_accept_mission(count=cls.thread_count)
