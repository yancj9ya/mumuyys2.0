from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec
from tool.wxocr.wxocr import WxOcr
from tool.Mytool.Counter import Counter
from tool.based.base.res.base_img import *
from task.ql.res.img_info import *
from task.ql.res.img_info_auto_create import *
from time import sleep, time, strftime, localtime
from PIGEON.log import log


class Ql(Click, ImageRec):
    def __init__(self, **kwargs):
        Click.__init__(self)
        ImageRec.__init__(self)
        self.uilist = [FIGHTING, ql_sb_ui, damo_ui, btn_tz_ui, ql_main_ui, QL_CG_1, ql_cg_t_ui]
        self.ui_delay = 0.5
        self.ocr = WxOcr()
        self.running = kwargs.get("STOPSIGNAL", True)
        self.cg_counter = Counter()
        self.times_counter = Counter()
        self.times = 0
        self.task_switch = True
        self.first_call = True

    def call_fire(self):
        if not self.match_img(ql_main_ui):
            return
        else:
            log.debug(f"@开始召唤契灵")
            # 点击召唤契灵入口
            self.area_click(CALL_ENTRANCE)
            sleep(1)
            # 选择镇墓兽
            self.area_click(CALL_TYPE_4)
            # 最大化数量
            self.area_click(CALL_NUM_MAX)
            # 点击召唤
            self.area_click(CALL_BTN)
            sleep(1)
            # 确认召唤
            self.area_click(CALL_CONFIRM)
        pass

    def main_ui(self):
        if self.first_call:
            self.first_call = False
            self.call_fire()
            log.debug(f"首次召唤完成 ")

        if res := self.match_img(ql_fire):
            self.area_click(res)
        else:
            log.debug(f"契灵未找到，开始召唤 ")
            self.call_fire()
            log.debug(f"召唤完成 ")

    def get_ball_num(self):
        """
        获取低级盘子的数量
        """
        if res := self.ocr.ocr((494, 22, 621, 57))["text"]:
            return int(res.split("/")[0])

    def challenge(self):
        """
        挑战页面的操作
        """
        if res := self.match_img(btn_tz_ui):  # 确保在挑战页面
            # 获取低级盘子的数量
            low_ball_num = self.get_ball_num()
            if self.times_counter.compare(self.times) or low_ball_num == 0:
                self.task_switch = False
                log.insert("2.2", f"@任务结束条件满足，退出任务 ")
                return
            else:
                # 点击挑战按钮
                self.area_click(res)
                log.insert("3.1", f"@第{self.times_counter.count:^3d}次挑战 ")

            # 处理提示弹窗
            sleep(1)
            if self.match_img(full_pan_continue_confirm):
                self.area_click(full_pan_continue_confirm[1])
            self.times_counter.increment()

    def run(self):
        sleep(self.ui_delay)
        match_result = self.match_ui(self.uilist, accuracy=0.85)
        log.insert("2.1", f"@匹配结果:{match_result} ")
        match match_result:
            case "FIGHTING":
                sleep(1)
            case "damo_ui" | "ql_sb_ui":
                self.area_click([990, 462, 1125, 520])
            case "ql_main_ui":
                self.main_ui()
            case "btn_tz_ui":
                self.challenge()
            case "QL_CG_1" | "ql_cg_t_ui":
                self.cg_counter.increment()
                # log.info(f'@捕获成功次数:{self.cg_counter.count}，概率：{self.cg_counter.count/self.times_counter.count*100:.2f}')
                self.area_click([646, 194, 724, 288])
            case _:
                pass
        pass

    def loop(self):
        while self.task_switch:
            match self.running.state:
                case "RUNNING":
                    self.run()
                    log.insert("4.1", f"@进度:{self.times_counter.count/self.times*100:.1f}%")
                    log.insert("5.1", f"@捕获次数:{self.cg_counter.count} ，捕获概率:{self.cg_counter.count/(self.times_counter.count+1)*100:.2f}%")
                case "STOP":
                    self.task_switch = False
                    log.insert("2.3", f"@任务已停止 ")
                    return
                case "WAIT":
                    sleep(1)
                    log.insert("2.1", f"@暂停中... ")
                    continue
                case _:
                    pass
        pass

    def set_parms(self, **kwargs):
        self.times = int(kwargs.get("times", 0))
        self.ui_delay = float(kwargs.get("ui_delay", 0.5))
        pass
