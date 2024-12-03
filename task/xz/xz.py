from Mytool.Click import Click
from Mytool.imageRec import ImageRec

from img.others.others_img_info import *
from time import sleep,time,strftime,localtime
from Mytool.Mylogger import *

class invitation:
    switch_code=True
    eye=ImageRec()
    hand=Click()
    @classmethod
    def invite_deamon(cls):
        try:
            # logger.info("协助邀请守护进程启动")
            while cls.switch_code:
                # logger.info(f'running,switch_code:{cls.switch_code}')
                sleep(3)#每三秒检测一次是否有邀请
                if res:=cls.eye.match_img(xz_yes):
                    logger.info("发现协助邀请")
                    if cls.eye.match_img(xz_no):
                        logger.info("确认协助邀请")
                        cls.hand.area_click(res)
                        logger.info("接受协助邀请")
        except Exception as e:
            logger.error(f"协助邀请守护进程异常:{e}")
        
   
    @classmethod
    def stop_deamon(cls):
        cls.switch_code=False
        logger.info("协助邀请守护进程结束")

    @classmethod
    def start_deamon(cls):
        cls.switch_code=True
        logger.info("协助邀请守护进程启动")
        cls.invite_deamon()