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
ui_map = {
    "ward_page": {
        "yyl_page": ward_page_TO_yyl_page,
    },
    "ql_page": {
        "ts_main_ui": ql_page_TO_ts_main,
    },
    "ltp_page": {
        "tp_main_ui": ltp_page_TO_tp_main,
    },
    "soul_content_page": {
        "home_page_unfold": soul_content_page_TO_home_page_unfold,
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
    },
    "home_page_fold": {
        "home_page_unfold": home_page_fold_TO_home_page_unfold,
    },
    "area_demon_ui": {
        "ts_main_ui": area_demon_TO_ts_main,
    },
}
for k, v in ui_map.items():
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
        self.ui = self.get_ui

    @property
    def get_ui(self):
        ui_keys = ui_list_keys.copy()[:-1]
        match_list = [ui_list[ui] for ui in ui_keys]
        return match_list

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

    def switch_to(self, target_ui):
        try:
            # 判断当前ui是否位于uimap，能够切换ui
            start_ui = self.find_current_ui()
            if start_ui is None:
                log.error(f"@SwitchUI:\n Can't find current ui,\n switch to {target_ui}")
                return False  # 找不到当前ui，无法切换

            # 如果当前ui即是目标ui，则直接返回
            if start_ui == target_ui:
                return True
            log.info(f"@SwitchUI:\n Current ui is {start_ui},\n switch to {target_ui}")

            # 寻找最短路径并执行切换操作
            while self.find_current_ui() != target_ui:
                if self.running.state == "STOP":
                    return True

                start_ui = self.find_current_ui()  # 获取当前的ui位置
                path = nx.shortest_path(G, start_ui, target_ui)  # 获得当前ui到目标ui的最短路径
                if not path:
                    raise Exception(f"Can't find path from {start_ui} to {target_ui}")
                log.info(f"[{start_ui}]->[{target_ui}] by path:{path}")

                # 遍历路径切换ui
                while start_ui != target_ui:
                    if self.running.state == "STOP":
                        return True

                    next_ui = path[path.index(start_ui) + 1]  # 获得下一个page
                    step = ui_map.get(start_ui, {}).get(next_ui)

                    if step is None:
                        raise Exception(f"Can't find step from {start_ui} to {next_ui}")

                    # 执行坐标点击之前先判断是否位于目标page:s_page
                    elif self.imageRec.match_img(ui_list[start_ui], accuracy=0.9):
                        if isinstance(step, list):
                            for p in step:
                                self.click.area_click(p)
                                sleep(0.8)
                        elif isinstance(step, tuple):
                            self.click.area_click(step)
                        elif isinstance(step, str):
                            res = self.imageRec.match_img(ui_list[step], accuracy=0.7)
                            if res:
                                self.click.area_click(res)
                        else:
                            raise Exception(f"Invalid step type: {type(step)}")
                        # 切换操作执行完成
                        sleep(1)

                    # 检测是否已经到达下一个页面
                    current_ui = self.find_current_ui()
                    if current_ui == next_ui:
                        start_ui = next_ui  # 切换成功，更新当前ui
                        continue
                    elif current_ui == start_ui:  # 仍然处于原页面，则继续循环
                        continue
                    elif current_ui not in path:  # 已经切换到其他不在路径的页面，跳出循环，重新寻找路径
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
