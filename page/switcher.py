from collections import deque
from PIGEON.log import log
from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec
from win11toast import toast
import time


class JumpAction:
    """跳转行为封装类"""

    CLICK_TYPE = "coordinates"
    IMAGE_TYPE = "image_based"
    XCLICK_TYPE = "xclick"

    def __init__(self, action_type, data, target_page):
        self.action_type = action_type
        self.data = data  # 坐标元组或图片标识
        self.target = target_page


class Page:
    def __init__(self, name, identifier):
        self.name = name
        self.identifier = identifier
        self.actions = {}  # {action_id: JumpAction}
        self.transitions = {}  # {target_page: Set(action_ids)}

    def add_action(self, action_id, action_type, data, target_page):
        """新增跳转动作"""
        action = JumpAction(action_type, data, target_page)
        self.actions[action_id] = action
        # 维护跳转关系图谱
        if target_page not in self.transitions:
            self.transitions[target_page] = set()
        self.transitions[target_page].add(action_id)


class PageNavigator:
    def __init__(self, timeout=30, retry=5, cooldown=1):
        self.cooldown = cooldown
        self.pages = {}
        self._current_page = None
        self.graph = {}  # 导航图谱 {source: {target: set(action_ids)}}
        self.timeout = timeout
        self.retry = retry
        self.CLICK = Click()
        self.IMG_REC = ImageRec()

    def register_page(self, page: Page):
        """注册页面并更新导航图谱"""
        self.pages[page.name] = page
        # 动态构建导航图谱
        self.graph[page.name] = page.transitions

    def _resolve_click(self, action: JumpAction):
        """智能解析点击坐标"""
        if action.action_type == JumpAction.CLICK_TYPE:
            return action.data
        elif action.action_type == JumpAction.IMAGE_TYPE:
            try:
                if isinstance(action.data, list):
                    if coords := self.IMG_REC.match_img(action.data):
                        # 针对一些特例处理
                        if action.data[2] in ["FENGMO", "SHADOW_GATE"]:
                            coords = (coords[0] + 188, coords[1] + 12, coords[2] + 158, coords[3] + 7)
                        return tuple(coords)
                elif isinstance(action.data, dict):
                    for img in action.data.values():
                        if coords := self.IMG_REC.match_img(img, accuracy=0.7):
                            return tuple(coords)
            except Exception as e:
                print(f"图像识别失败：{e}")
                self.CLICK.win.del_cache()

    def smart_goto(self, target_page, task_switch):
        """智能路径导航"""
        current_retry = 1
        # 寻找路径
        while current_retry <= self.retry:
            match task_switch.state:
                case "STOP":
                    log.info("已停止页面切换")
                    return False
                case "WAIT":
                    log.info("暂停页面切换")
                    continue
                case "RUNNING":
                    log.info(f"正在寻找路径，目标页面：{target_page}")
            try:
                # 刷新当前页面
                self.refresh_current_page()
                # 如果当前页面为目标页面，直接返回
                if self.current_page.name == target_page:
                    log.info(f"当前页面为目标页面，无需跳转")
                    return True
                if path := self.find_path(target_page):
                    while self.current_page.name != target_page:
                        current_index = path.index(self.current_page)
                        next_page = path[current_index + 1]
                        transitions = self.graph[self.current_page.name].get(next_page, set())
                        print(f"current:{self.current_page.name}->{next_page.name} by trans:{transitions}")
                        for action_id in transitions:
                            action = self.current_page.actions[action_id]
                            try:
                                if self._execute_jump(action):
                                    print(f"成功跳转到 {next_page.name}")
                                    success = True
                                    current_retry = 1  # 重置重试次数
                                    break
                                else:
                                    print(f"无法执行跳转动作: {action_id}-{action.action_type}")
                                    success = False
                            except Exception as e:
                                print(f"跳转出现错误: {str(e)}")

                        if not success:
                            raise RuntimeError(f"无法到达 {next_page.name}")
                        # 更新当前页面
                        self.refresh_current_page()
                    else:
                        return True
                else:
                    raise ValueError("不存在有效路径")
            except Exception as e:
                log.info(f"第 {current_retry} 次尝试失败: {str(e)}")
                current_retry += 1
                time.sleep(self.cooldown * current_retry)  # 指数退避
                if current_retry == self.retry - 1:
                    toast(f"无法到达 {target_page}，请检查页面配置", scenario="incomingCall", button="继续")
                continue
        else:
            toast(f"最终尝试失败，无法到达 {target_page}，请检查页面配置")

    def _try_back(self):
        """尝试回退到上一页面"""

        pass

    def _execute_jump(self, action: JumpAction):
        current_tries = 0
        while current_tries < 3:
            try:
                """执行单次跳转"""
                if action.action_type == JumpAction.XCLICK_TYPE:
                    self.CLICK.xclick()
                    time.sleep(1)
                    return True
                coords = self._resolve_click(action)
                if not coords:
                    return False
                if isinstance(coords, tuple):
                    self.CLICK.area_click(coords)
                    time.sleep(0.5)
                elif isinstance(coords, list):
                    for coor in coords:
                        self.CLICK.area_click(coor)
                        time.sleep(0.5)

                start = time.time()
                while time.time() - start < self.timeout:
                    """检测页面是否跳转成功"""
                    time.sleep(0.5)
                    current = self.detect_page()
                    if current == None:  # 页面识别失败，返回None,可能位于页面跳转之中，等待0.2s之后再次检查页面
                        time.sleep(1)
                        continue
                    elif current == self.current_page.name:  # 仍然处于原来的页面，未跳转成功
                        raise LookupError(f"仍处于原页面{current}，尝试重新执行跳转")  # 抛出异常触发重试机制
                    elif current == action.target.name:  # 页面跳转成功
                        """页面跳转成功"""
                        log.info(f"跳转成功，当前页面：{current}")
                        return True
                    elif current in self.graph.keys():  # 跳到其他已知页面需要重新规划路径
                        return False
                else:  ### 页面跳转超时，返回False
                    print("页面跳转超时")
                    return False
            except Exception as e:
                print(e)
                current_tries += 1
                time.sleep(1 * current_tries)

    def detect_page(self):
        """页面识别核心逻辑"""
        try:
            for page in self.pages.values():
                if self.IMG_REC.match_img(page.identifier):
                    return page.name
            raise LookupError("未知页面状态")
        except Exception as e:
            print(f"页面识别失败：{e}")
            self.CLICK.win.del_cache()

    @property
    def current_page(self):
        """自动获取当前页面的属性访问器"""
        if self._current_page is None:
            self.refresh_current_page()
        return self._current_page

    @current_page.setter
    def current_page(self, value):
        """允许手动设置当前页面（调试用）"""
        if isinstance(value, str):
            self._current_page = self.pages[value]
        elif isinstance(value, Page):
            self._current_page = value
        else:
            raise TypeError("必须使用页面名称或Page对象")

    def refresh_current_page(self):
        """强制刷新当前页面检测"""
        try:
            page_name = self.detect_page()
            self._current_page = self.pages[page_name]
        except LookupError:
            raise RuntimeError("当前不在任何已知页面")

    def get_page_by_name(self, name: str):
        # print(self.pages)
        for page in self.pages.values():
            # print(page.name)
            if page.name == name:
                return page

        raise ValueError(f"未找到名为 {name} 的页面")

    def find_path(self, target_name):
        """使用BFS算法寻找最短路径"""

        # 实时扫描当前页面状态
        self.refresh_current_page()

        target = self.get_page_by_name(target_name)
        start_name = self.current_page
        visited = {start_name: None}
        queue = deque([start_name])

        # 打印调试信息
        log.info("\n[路径搜索] 寻找路径: {} -> {}".format(start_name.name, target.name))
        # print("当前导航图谱:", self._get_graph_debug_info())

        while queue:
            current = queue.popleft()
            if current == target:
                return self._reconstruct_path(visited, target)

            # 获取该页面所有可达页面名称
            neighbors = self.graph.get(current.name, {}).keys()
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited[neighbor] = current
                    queue.append(neighbor)
                    print(f"  ├─ 发现路径: {current.name} → {neighbor.name}")

        # 输出完整导航图供调试
        print("[错误诊断] 当前导航图状态:")
        for page, links in self.graph.items():
            print(f"  {page}: {[page.name for page in links.keys()]}")
        raise ValueError("路径不存在. 可能原因：\n" "1. 目标页面未注册\n" "2. 中间页面缺少跳转动作\n" "3. 页面标识符配置错误")

    def _get_graph_debug_info(self):
        """生成导航图的调试信息"""
        graph_info = {}
        for page in self.graph:
            graph_info[page] = [page.name for page in self.graph[page].keys()]
        return graph_info

    def _reconstruct_path(self, visited, target):
        """回溯构建完整路径"""
        print(f"[路径回溯] 回溯路径:{[f'{s.name}->{e.name if e else None}' for s,e in visited.items()]}")
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = visited[current]
        log.info(f"[路径回溯] 最终路径:{'→'.join([p.name for p in path[::-1]])}")
        return path[::-1]

    def switch_to(self, target, task_switch):
        return self.smart_goto(target, task_switch)


# 使用示例
if __name__ == "__main__":
    # 定义页面
    main = Page("main", "main_screen.png")
    main.add_action("go_shop1", JumpAction.CLICK_TYPE, (100, 200), "shop")
    main.add_action("go_shop2", JumpAction.IMAGE_TYPE, "shop_icon.png", "shop")

    shop = Page("shop", "shop_verify.png")
    shop.add_action("back_main", JumpAction.IMAGE_TYPE, "return_button.png", "main")
    shop.add_action("go_arena", JumpAction.CLICK_TYPE, (300, 500), "arena")

    # 初始化导航
    nav = PageNavigator()
    nav.register_page(main)
    nav.register_page(shop)
    nav.current_page = main

    # 执行智能跳转
    try:
        nav.smart_goto("arena")  # 自动路径：main -> shop -> arena
        print("导航成功")
    except Exception as e:
        print(f"导航失败: {str(e)}")
