import networkx as nx
from time import sleep
from task.based.switchui.res.switch_img_info import *
from task.based.switchui.res.page_switch_coord import *
from task.based.Mytool.Click import Click
from task.based.Mytool.imageRec import ImageRec
from PIGEON.log import log

# import matplotlib.pyplot as plt
# 构建切换ui的路径图，主要是为了寻找最短路径
G = nx.Graph()
for img_ui in ui_list_keys:
    G.add_node(img_ui)
G.add_edge("tp_main_damo", "tp_main_ui", weight=1)  # 突破达摩到突破主界面
G.add_edge("tp_main_ui", "ts_main_ui", weight=1)  # 突破主界面到探索界面
G.add_edge("tp_end_mark_ui", "tp_main_ui", weight=1)  # 突破结束到突破主界面
G.add_edge("ts_main_ui", "ts_tz_ui", weight=1)  # 探索界面到探索挑战界面
G.add_edge("ts_tz_ui", "ts_cm_ui", weight=1)  # 探索挑战界面到副本困28界面
G.add_edge("ts_cm_ui", "ts_tz_ui", weight=2)  # 副本困28界面到探索挑战界面
G.add_edge("ts_end_mark_ui", "ts_cm_ui", weight=1)  # 探索结束到副本困28界面
G.add_edge("home_page_fold", "home_page_unfold", weight=1)
G.add_edge("home_page_unfold", "ts_main_ui", weight=1)  # home到突破主界面
G.add_edge("ts_main_ui", "area_demon_ui", weight=1)  # 探索界面到地鬼界面

# 根据最短路径具体需要实施的每一步切换的点击操作的坐标
ui_map = {
    "tp_main_ui": {
        "ts_main_ui": tp_main_TO_ts_main,
    },
    "ts_main_ui": {
        "ts_tz_ui": ts_cm_TO_ts_tz,
        "tp_main_ui": ts_main_TO_tp_main,
        "area_demon_ui": ts_main_TO_area_demon,
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
    "home_page_unfold": {
        "ts_main_ui": home_page_unfold_TO_ts_main,
    },
    "home_page_fold": {
        "home_page_unfold": home_page_fold_TO_home_page_unfold,
    },
    "area_demon_ui": {
        "ts_main_ui": area_demon_TO_ts_main,
    },
}


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

    def find_current_ui(self):  # 寻找当前的ui
        for key in ui_map:
            if self.imageRec.match_img(ui_list[key]):
                return key
            sleep(0.1)

    def switch_to(self, target_ui):
        try:
            # 判断当前ui是否位于uimap，能够切换ui
            if start_ui := self.find_current_ui():
                # 如果当前ui即是目标ui，则直接返回
                if start_ui == target_ui:
                    return True
                log.info(f"@SwitchUI:\n Current ui is {start_ui},\n switch to {target_ui}")
            else:
                log.error(f"@SwitchUI:\n Can't find current ui,\n switch to {target_ui}")
                return False  # 找不到当前ui，无法切换

            # 寻找最短路径并执行切换操作
            while self.find_current_ui() != target_ui:
                if not self.running.is_set():
                    break  # 停止运行
                start_ui = self.find_current_ui()  # 获取当前的ui位置
                path = nx.shortest_path(G, start_ui, target_ui)  # 获得当前ui到目标ui的最短路径
                if path is None:
                    # print(f"Can't find path from {start_ui} to {target_ui}")
                    raise Exception("Can't find path")
                log.info(f"[{start_ui}]->[{target_ui}] by path:{path}")
                # 根据最短路径和uimap循环执行操作直到到达最终的目标ui
                s_page = path.pop(0)  # 当前page
                next_page = path.pop(0)  # 下一个page
                while s_page != target_ui:
                    if not self.running.is_set():
                        break  # 停止运行
                    step = ui_map[s_page].get(next_page, None)  # 获取过程坐标
                    # 执行坐标
                    if step is None:
                        raise Exception(f"Can't find step from {s_page} to {next_page}")
                    if type(step) == list:
                        for p in step:
                            self.click.area_click(p)
                            sleep(0.8)
                    elif type(step) == tuple:
                        self.click.area_click(step)
                    elif type(step) == str:
                        if res := self.imageRec.match_img(ui_list[step], accuracy=0.7):
                            self.click.area_click(res)
                    else:
                        raise Exception(f"Invalid step type: {type(step)}")
                    sleep(1)
                    # 检测是否已经位于目标page:next_page
                    if self.find_current_ui() == next_page:
                        # 如果已经位于目标page:next_page，则继续循环执行
                        s_page = next_page
                        next_page = path.pop(0) if path else None  # 获得下一个page
                        continue
                    elif self.find_current_ui() == s_page:
                        continue
                    elif self.find_current_ui() not in path + [next_page]:
                        log.error(f"@SwitchUI:current_ui is not in path,need to re-find path")
                        break
                else:
                    log.info(f"Switch to {target_ui} success")
                    return True  # 切换成功，返回True

        except Exception as e:
            log.error(f"@SwitchUI: {e}")

    # def draw_map(self):
    #    nx.draw(G, with_labels=True, node_color="lightblue", node_size=700, font_weight="bold")
    #    plt.show()


if __name__ == "__main__":
    import os

    os.path.append("D:\python\mumuyys2.0\\")

    swtich = SwitchUI()
    swtich.switch_to("ts_main_ui")
