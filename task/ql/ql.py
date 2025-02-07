from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec
from tool.Mytool.Ocr import Ocr
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
        self.uilist = [FIGHTING, ql_sb_ui, damo_ui, btn_tz_ui, ql_main_ui, ql_cg_ui, ql_cg_t_ui, ql_sb_ui]
        self.ui_delay = 0.5
        self.running = kwargs.get("STOPSIGNAL", True)
        self.cg_counter = Counter()
        self.times_counter = Counter()
        self.times = 0
        self.call_fire_times = 0
        self.task_switch = True

    def call_fire(self):
        if not self.match_img(ql_main_ui):
            return
        else:
            for call_times in range(5):
                log.debug(f"@第{call_times+1}次召唤 ")
                self.area_click([1171, 475, 1201, 504])
                sleep(0.5)
                if call_times == 0:
                    self.area_click([933, 279, 1044, 405])
                self.area_click([1149, 611, 1219, 658])
                sleep(1)
            self.call_fire_times += 5
        pass

    def main_ui(self):
        if res := self.match_img(ql_fire):
            self.area_click(res)
        else:
            log.debug(f"契灵未找到，开始召唤 ")
            self.call_fire()
            log.debug(f"召唤完成，共召唤{self.call_fire_times}次 ")

    def run(self):
        sleep(self.ui_delay)
        match_result = self.match_ui(self.uilist, accuracy=0.9)
        log.insert("2.1", f"@匹配结果:{match_result} ")
        match match_result:
            case "FIGHTING":
                sleep(1)
            case "damo_ui" | "ql_sb_ui":
                self.area_click([990, 462, 1125, 520])
            case "ql_main_ui":
                self.main_ui()
            case "btn_tz_ui":
                if res := self.match_img(btn_tz_ui):
                    if self.times_counter.compare(self.times):
                        self.task_switch = False
                        log.insert("2.2", f"@挑战次数已达{self.times}次，退出任务 ")
                        return
                    self.area_click(res)
                    sleep(1)
                    if self.match_img(full_pan_continue_confirm):
                        self.area_click(full_pan_continue_confirm[1])
                    self.times_counter.increment()
                    log.insert("3.1", f"@第{self.times_counter.count:^3d}次挑战 ")
            case "ql_cg_ui" | "ql_cg_t_ui":
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
