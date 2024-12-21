import networkx as nx
import traceback
from time import sleep
from task.based.switchui.res.switch_img_info import *
from task.based.switchui.res.page_switch_coord import *
from task.based.Mytool.Click import Click
from task.based.Mytool.imageRec import ImageRec
from PIGEON.log import log
from PIGEON.retry import retry


# import matplotlib.pyplot as plt
# 构建切换ui的路径图，主要是为了寻找最短路径
G = nx.Graph()
# for img_ui in ui_list_keys:
#     G.add_node(img_ui)
ui_map = {
    "server_page": {
        "home_page_fold": server_TO_home_page_fold,
    },
    "fm_page": {
        "backstreet_page": BACK,
    },
    "backstreet_page": {
        "fm_page": backstreet_page_TO_fm_page,
        "home_page_unfold": BACK,
    },
    "ward_page": {
        "yyl_page": ward_page_TO_yyl_page,
    },
    "ql_page": {
        "ts_main_ui": ql_page_TO_ts_main,
        # "soul_content_page": SOUL_CONTENT,
    },
    "ltp_page": {
        "tp_main_ui": ltp_page_TO_tp_main,
    },
    "soul_content_page": {  # 式神录
        "home_page_unfold": soul_content_page_TO_home_page_unfold,
        # "tp_main_ui": soul_content_page_TO_home_page_unfold,
        # "fm_page": soul_content_page_TO_home_page_unfold,
        # "ql_page": soul_content_page_TO_home_page_unfold,
    },
    "dg_chose_page": {
        "shenshe_page": dg_chose_page_TO_shenshe_page,
    },
    "yyl_page": {
        "shenshe_page": yyl_page_TO_shenshe_page,
        "home_page_unfold": yyl_page_TO_home_page_unfold,
        "ward_page": yyl_page_TO_ward_page,
    },
    "shenshe_page": {
        "dg_chose_page": shenshe_page_TO_dg_chose_page,
        "yyl_page": shenshe_page_TO_yyl_page,
    },
    "tp_main_ui": {
        "ts_main_ui": tp_main_TO_ts_main,
        "ltp_page": tp_main_TO_ltp_page,
        # "soul_content_page": SOUL_CONTENT,
    },
    "ts_main_ui": {  # 探索界面
        "ts_tz_ui": ts_cm_TO_ts_tz,
        "tp_main_ui": ts_main_TO_tp_main,
        "area_demon_ui": ts_main_TO_area_demon,
        "home_page_unfold": ts_main_TO_home_page_unfold,
        "ql_page": ts_main_TO_ql_page,
    },
    "ts_tz_ui": {
        "ts_cm_ui": ts_tz_TO_ts_cm,
        "ts_main_ui": ts_tz_TO_ts_main,
    },
    "ts_cm_ui": {"ts_tz_ui": ts_cm_TO_ts_tz},
    "tp_end_mark_ui": {
        "tp_main_ui": tp_end_mark_TO_tp_main,
    },
    "ts_end_mark_ui": {
        "ts_cm_ui": ts_end_mark_TO_ts_cm,
    },
    "tp_main_damo": {
        "tp_main_ui": tp_damo_TO_tp_main,
    },
    "home_page_unfold": {  # 主页展开
        "ts_main_ui": home_page_unfold_TO_ts_main,
        "yyl_page": home_page_unfold_TO_yyl_page,
        "soul_content_page": home_page_unfold_TO_soul_content_page,
        "backstreet_page": home_page_unfold_TO_backstreet_page,
    },
    "home_page_fold": {
        "home_page_unfold": home_page_fold_TO_home_page_unfold,
    },
    "area_demon_ui": {
        "ts_main_ui": area_demon_TO_ts_main,
    },
}

for k, v in ui_map.items():
    G.add_node(k)
    for e_k, e_v in v.items():
        G.add_edge(k, e_k, weight=len(e_v))


class SwitchUI:
    _instance = None

    def __new__(cls, *arg, **kw):  # 确保只有一个实例
        if not cls._instance:
            cls._instance = super(SwitchUI, cls).__new__(cls)
        return cls._instance

    def __init__(self, running=None):
        self.click = Click()
        self.imageRec = ImageRec()
        self.running = running
        self.ui = self.get_ui()

    def get_ui(self):
        match_list = []
        for ui in ui_map.keys():
            match_list.append(ui_list[ui])
        return match_list

    def try_back_step(self, *args, **kwargs):
        print("try back")
        for k, v in BACK.items():
            if res := self.imageRec.match_img(v, accuracy=0.9):
                self.click.area_click(res)
                sleep(1)
        pass

    # @retry(max_retries=5, delay=0.5)
    def find_current_ui(self):  # 寻找当前的ui
        if res := self.imageRec.match_ui(self.ui, accuracy=0.7):
            return res
        else:
            return None

    def generate_shortest_path(self, start_ui, target_ui):
        shortest_path = nx.shortest_path(G, start_ui, target_ui)
        if shortest_path:
            return shortest_path
        else:
            return None

    def exute_step(self, step):
        if isinstance(step, list):
            for p in step:
                self.click.area_click(p)
                sleep(0.8)
        elif isinstance(step, tuple):
            self.click.area_click(step)
        elif isinstance(step, str):
            res = self.imageRec.match_img(ui_list[step], accuracy=0.8)
            if res:
                self.click.area_click(res)
        elif isinstance(step, dict):
            for k, v in step.items():
                if res := self.imageRec.match_img(v, accuracy=0.9):
                    self.click.area_click(res)
        else:
            raise Exception(f"Invalid step type: {type(step)}")

    def confirm_page(self, need_confirm_page):
        if self.imageRec.match_img(ui_list[need_confirm_page], accuracy=0.8):
            return True
        else:
            return False
        pass

    @retry(max_retries=10, delay=1)
    def switch_to(self, target_ui):
        try:
            if self.running.state == "STOP":
                print(f"STOP_SWITCH_UI: {target_ui}")
                return True
            log.info(f"@SwitchUI:Start switch to {target_ui}")
            # 判断当前ui是否位于uimap，能够切换ui
            start_ui = self.find_current_ui()  # 获取当前的ui位置
            if start_ui is None:
                log.error(f"@SwitchUI:\n Can't find current ui,\n switch to {target_ui}")
                self.try_back_step()  # 找不到当前ui，无法切换
                raise Exception(f"Can't find current ui")
            # 如果当前ui即是目标ui，则直接返回
            elif start_ui == target_ui:
                log.info(f"@SwitchUI:already into page {target_ui}")
                return True
            else:
                log.info(f"@SwitchUI:Current{start_ui}->{target_ui}")
        except Exception as e:
            log.error(f"@SwitchUI: {e}\nfull stack:\n{traceback.format_exc()}")
            raise e
        try:
            path = self.generate_shortest_path(start_ui, target_ui)  # 获得当前ui到目标ui的最短路径
            if not path:
                raise Exception(f"Can't find path from {start_ui} to {target_ui}")
            else:
                log.info(f"[{start_ui}]->[{target_ui}] by path:{path}")
            while self.find_current_ui() != target_ui:
                if self.running.state == "STOP":
                    return True
                # 遍历路径切换ui
                next_ui = path[path.index(start_ui) + 1]  # 获得下一个page
                step = ui_map.get(start_ui, {}).get(next_ui)

                if step is None:
                    raise Exception(f"STPE_ERROR: {start_ui} to {next_ui}")
                if self.confirm_page(start_ui):
                    self.exute_step(step)
                    sleep(1)
                    # 检测是否已经到达下一个页面
                    current_ui = self.find_current_ui()
                    if current_ui == next_ui:
                        start_ui = next_ui  # 切换成功，更新当前ui
                        continue
                    elif current_ui == start_ui:  # 仍然处于原页面，则继续循环
                        continue
                    elif current_ui is None:  # 未知的页面，可能是正处于切换动画中，继续循环
                        sleep(1)
                        continue
                    elif current_ui not in path:  # 已经切换到其他不在路径的页面，跳出循环，重新寻找路径
                        raise Exception(f"Unknown page {current_ui} not in path,need to refind path")
                elif self.confirm_page(next_ui):
                    start_ui = next_ui  # 切换成功，更新当前ui
                    continue

                else:
                    print(f"Confirm page {start_ui} failed")
                #     # for k, v in BACK.items():
                #     #     if res := self.imageRec.match_img(v, accuracy=0.9):
                #     #         self.click.area_click(res)
                #     #         sleep(1)
                #     raise Exception(f"Confirm page {start_ui} failed")
            else:
                log.info(f"Switch to {target_ui} success")
                return True  # 切换成功，返回True
        except Exception as e:
            log.error(f"@SwitchUI: {e}\nfull stack:\n{traceback.format_exc()}")
            raise e
