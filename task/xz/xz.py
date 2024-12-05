from task.based.Mytool.Click import Click
from task.based.Mytool.imageRec import ImageRec

from task.xz.res.others_img_info import *
from time import sleep, time, strftime, localtime
from PIGEON.log import log


class Xz:
    running = None
    eye = ImageRec()
    hand = Click()
    count = 0

    @classmethod
    def invite_deamon(cls):
        try:
            # log.info("协助邀请守护进程启动")
            while cls.running.is_set():
                # log.info(f'running,switch_code:{cls.switch_code}')
                sleep(3)  # 每三秒检测一次是否有邀请
                if res := cls.eye.match_img(xz_yes):
                    log.info("发现协助邀请")
                    if cls.eye.match_img(xz_no):
                        log.info("确认协助邀请")
                        cls.hand.area_click(res)
                        log.info("接受协助邀请")
                        cls.count += 1
            log.info(f"协助邀请守护进程结束,共接受邀请{cls.count}次")
            cls.count = 0

        except Exception as e:
            log.error(f"协助邀请守护进程异常:{e}")

    @classmethod
    def start_deamon(cls, **kwargs):
        cls.running = kwargs.get("STOPSIGNAL", True)
        log.info("协助邀请守护进程启动")
        cls.invite_deamon()
