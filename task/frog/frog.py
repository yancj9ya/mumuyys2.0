from tool.Mytool.Click import Click
from tool.Mytool.imageRec import ImageRec
from task.frog.spider_info import DynamicCollector
from PIGEON.reqai import ReqAI
import asyncio, json
from datetime import datetime, timedelta, time
from PIGEON.log import log
from time import sleep
from task.frog.res.img_info_auto_create import *


class HandConfig:
    def write_config(self, config_file_path="task/frog/config/up_config.json"):
        """
        写入配置文件。

        该函数将当前对象的属性值写入指定的 JSON 配置文件中。

        Parameters:
            config_file_path (str): 配置文件的路径，默认为 "config.json"

        Returns:
            None
        """
        with open(config_file_path, "w", encoding="utf-8") as file:
            json.dump(self.config_data, file, ensure_ascii=False, indent=4)
        pass

    def load_config(self, config_file_path="task/frog/config/up_config.json"):
        """
        加载配置文件。

        该函数从指定的 JSON 配置文件中读取各项参数，并将其赋值给相应的变量。

        Parameters:
            config_file_path (str): 配置文件的路径，默认为 "config.json"

        Returns:
            None

        Raises:
            FileNotFoundError: 如果配置文件不存在
            json.JSONDecodeError: 如果配置文件格式不正确
        """
        try:
            with open(config_file_path, "r", encoding="utf-8") as file:
                self.config_data = json.load(file)
                self.uid_name = {name_data["uid"]: name for name, name_data in self.config_data["up_list"].items()}
                self.rate = {name: (name_data["win_times"] / (name_data["win_times"] + name_data["lose_times"])) for name, name_data in self.config_data["up_list"].items()}
                # print(f"rate: {self.rate}")
        except FileNotFoundError:
            print(f"配置文件 {config_file_path} 未找到。")
            raise
        except json.JSONDecodeError as e:
            print(f"配置文件 {config_file_path} 格式错误：{str(e)}")
            raise


class HandTime:
    def str_to_time(self, time_str: str) -> datetime:
        """
        将字符串格式的时间转换为 datetime 格式。

        该函数将字符串格式的时间（格式为'YYYY-MM-DD HH:MM:SS'）转换为 datetime 格式。

        Parameters:
            time_str (str): 字符串格式的时间

        Returns:
            datetime: datetime 格式的时间

        Raises:
            ValueError: 如果字符串格式的时间格式不正确
        """
        try:
            return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError(f"字符串格式的时间 {time_str} 格式不正确，应为'YYYY-MM-DD HH:MM:SS'")

    def time_to_str(self, time: datetime) -> str:
        """
        将 datetime 格式的时间转换为字符串格式。

        该函数将 datetime 格式的时间转换为字符串格式（格式为'YYYY-MM-DD HH:MM:SS'）。

        Parameters:
            time (datetime): datetime 格式的时间

        Returns:
            str: 字符串格式的时间
        """
        return time.strftime("%Y-%m-%d %H:%M:%S")

    import datetime

    def calculate_next_runtime(self):
        now = datetime.now()
        today = now.date()
        candidate_hours = [11, 13, 15, 17, 19, 21, 23]

        # 生成当天和次日的候选时间
        today_candidates = [datetime.combine(today, time(h, 55)) for h in candidate_hours]
        tomorrow = today + timedelta(days=1)
        tomorrow_candidates = [datetime.combine(tomorrow, time(h, 55)) for h in candidate_hours]
        all_candidates = sorted(today_candidates + tomorrow_candidates)

        # 找到第一个大于等于当前时间的候选时间
        candidate = None
        for t in all_candidates:
            if t >= now:
                candidate = t
                break
        else:
            candidate = datetime.combine(tomorrow + timedelta(days=1), time(11, 55))

        # 检查是否在押注窗口内
        window_start = candidate
        window_end = candidate + timedelta(minutes=5)
        if window_start <= now < window_end:
            # 寻找下一个候选时间
            index = all_candidates.index(candidate)
            if index < len(all_candidates) - 1:
                candidate = all_candidates[index + 1]
            else:
                # 处理跨两日的情况
                next_day = candidate.date() + timedelta(days=1)
                candidate = datetime.combine(next_day, time(11, 55))

        # 计算时间差
        delta = candidate - now
        if delta.total_seconds() < 0:
            return "00:00:00"

        total_seconds = int(delta.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def check_time(self):
        """
        计算当前时间是否位于竞猜押注的时间区间（example:11:55-12:00),如果位于则返回false,否则返回当前到可押注起始时间的剩余时间。

        该函数首先获取当前时间，并根据当前时间是否在上午10点之前来决定计算到哪个目标时间的剩余时间。
        如果当前时间在上午10点之前，计算到当天11点50分的时间差。
        如果当前时间在上午10点之后，函数会进入活动时间处理逻辑，确定当前时间所在的时间区间，并计算到该区间结束前5分钟开始时间的剩余时间。
        如果当前时间处于区间的最后5分钟内，函数返回False；否则，返回格式化的剩余时间字符串。

        Parameters:
            无

        Returns:
            str: 格式化的剩余时间字符串，格式为'HH:MM:SS'；或者在特定条件下返回False。
        """
        now = datetime.now()
        current_hour = now.hour
        today_10am = datetime(now.year, now.month, now.day, 10)

        # 如果当前时间在10点前，计算到当天11:55的时间差
        if now < today_10am:
            target_time = today_10am.replace(hour=11, minute=55, second=0)
            delta = target_time - now
        else:
            # 处理活动时间内（10:00-24:00）的逻辑
            start_h = (current_hour // 2) * 2  # 计算当前时间所在区间的起始小时
            # 确保起始小时不小于10
            if start_h < 10:
                start_h = 10

            # 计算当前区间的结束时间（处理跨天）
            end_h = start_h + 2
            days_add_end, end_h = divmod(end_h, 24)
            end_time = datetime(now.year, now.month, now.day) + timedelta(days=days_add_end, hours=end_h)

            # 当前区间的最后5分钟开始时间
            start_last_5min = end_time - timedelta(minutes=5)

            if start_last_5min <= now < end_time:
                return False
            else:
                # 不在最后5分钟内，计算到当前区间最后5分钟的时间差
                if now < start_last_5min:
                    delta = start_last_5min - now
                else:
                    # 当前时间超过当前区间，直接返回0（理论上不会发生）
                    delta = timedelta(0)

        # 格式化时间差为HH:MM:SS
        total_seconds = delta.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"


class Frog(HandTime, HandConfig):
    def __init__(self, **kwargs):
        self.click = Click()
        self.image_rec = ImageRec()
        self.ai = ReqAI()
        self.uilist = [bet_lose, bet_win, frog, bet_on_confirm, bet_on, bet_done, bet_hall]
        self.task_switch = True
        self.running = kwargs.get("STOPSIGNAL", None)
        self.ui_delay = 0.5
        self.load_config()

    def set_parms(self, **kwargs):
        self.ui_delay = float(kwargs.get("ui_delay", 1))

    def loop(self):
        if time_delta := self.check_time():
            log.info(f"距离下一轮押注还有{time_delta} ")
            self.next_time = time_delta
            return
        else:
            # 获取up结果并解析
            self.finnal_result = self.parse_answer()
        while self.task_switch:
            match self.running.state:
                case "RUNNING":
                    self.run()
                case "STOP":
                    self.task_switch = False
                    log.insert("2.3", f"@任务已停止 ")
                    return
                case "WAIT":
                    sleep(1)
                    continue
                case _:
                    pass
        return
        pass

    def get_last_res_and_update_rate(self):
        try:
            # 获取上一次押注结果
            if self.image_rec.match_img(bet_res_btn):
                self.click.area_click(bet_res_btn[1])

                for _ in range(2):
                    sleep(1)
                    red_bet = self.image_rec.match_img(on_red)
                    blue_bet = self.image_rec.match_img(on_blue)
                    _res_win = self.image_rec.match_img(res_win, accuracy=0.8)
                    _res_lose = self.image_rec.match_img(res_lose, accuracy=0.8)
                log.file(f"red_bet: {red_bet}, blue_bet: {blue_bet}, res_win: {_res_win}, res_lose: {_res_lose}")
                # 解析结果
                match (bool(red_bet), bool(blue_bet), bool(_res_win), bool(_res_lose)):
                    case (True, False, True, False) | (False, True, False, True):
                        self.last_res = "red"
                    case (True, False, False, True) | (False, True, True, False):
                        self.last_res = "blue"
                    case _:
                        log.info(f"未知结果: red_bet: {red_bet}, blue_bet: {blue_bet}, res_win: {_res_win}, res_lose: {_res_lose}")
                        self.last_res = None
                # 更新rate
                # 更新的时间条件，防止重复更新，造成数据误差
                last_update_time = self.str_to_time(self.config_data["update_rate_time"])
                if (datetime.now() - last_update_time).total_seconds() > 6900:  # 2小时
                    log.info("开始更新rate")
                    # 更新rate
                    for name in self.config_data["up_list"].keys():
                        if self.last_res == "red" and name in self.config_data["last_bet"]["red_up_list"]:  # 红胜 压红的胜场+1
                            self.config_data["up_list"][name]["win_times"] += 1
                        elif self.last_res == "red" and name in self.config_data["last_bet"]["blue_up_list"]:  # 红胜 压蓝的负场+1
                            self.config_data["up_list"][name]["lose_times"] += 1
                        elif self.last_res == "blue" and name in self.config_data["last_bet"]["blue_up_list"]:  # 蓝胜 压蓝的胜场+1
                            self.config_data["up_list"][name]["win_times"] += 1
                        elif self.last_res == "blue" and name in self.config_data["last_bet"]["red_up_list"]:  # 蓝胜 压红的负场+1
                            self.config_data["up_list"][name]["lose_times"] += 1
                        else:
                            log.info(f"未知结果{name}:{self.last_res}")
                    # 保存并更新时间
                    self.config_data["update_rate_time"] = self.time_to_str(datetime.now())
                    self.write_config()
                else:
                    log.info(f"距离上次更新rate时间不足2小时，不更新rate")
                log.info(f"上一次押注结果: {self.last_res}")
            else:
                log.info("未找到上一次押注结果按钮")
        except Exception as e:
            log.error(f"获取上一次押注结果失败: {str(e)}")
        finally:
            if self.image_rec.match_img(exit_res_state):
                self.click.area_click(exit_res_state[1])
        pass

    def run(self):
        sleep(self.ui_delay)
        res = self.image_rec.match_ui(self.uilist)
        log.insert("2.1", f"UI match: {res} ")
        match res:
            case "bet_done":
                self.next_time = self.calculate_next_runtime()
                self.task_switch = False
            case "bet_win":
                self.click.area_click(box[1])
                self.click.area_click(next_turn[1])
            case "bet_lose":
                self.click.area_click(next_turn[1])
            case "frog":
                self.click.area_click(frog[1])
            case "bet_on_confirm":
                self.click.area_click(bet_on_confirm[1])
            case "bet_hall":
                # 获取上次结果并更新rate
                if not hasattr(self, "last_res"):
                    self.get_last_res_and_update_rate()
                    return
                # 获取决定下注的位置, 并点击
                if self.finnal_result == "red":
                    self.click.area_click(left[1])
                elif self.finnal_result == "blue":
                    self.click.area_click(right[1])
                else:
                    log.info("获取押注结果失败")
                sleep(1)
                pass
            case "bet_on":
                # 首先选择30w
                # 如果30w没选中，则先点击30w
                if not self.image_rec.match_img(coin_30_on) and self.image_rec.match_img(coin_30_not_on):
                    self.click.area_click(coin_30[1])
                    log.info("选择30w")
                elif self.image_rec.match_img(coin_30_on):
                    self.click.area_click(bet_on[1])
                    log.info(f"确认下注: {self.finnal_result}")
                else:
                    log.info("未知结果")
                # 点击确认
        pass

    async def get_info(self):
        # 自定义UID映射（可选）

        async with DynamicCollector(uid_mapping=self.uid_name) as collector:
            try:
                data = await collector.fetch_data()
                return data if data else []
            except Exception as e:
                log.info(f"数据获取失败: {str(e)}")
        pass

    def conc_text(self) -> str:
        data = asyncio.run(self.get_info())

        # 检查数据是否为空
        if not data:
            log.info("没有获取到数据")
            return

        # 写入文件并构建问题字符串
        file_path = "task/frog/info_count.txt"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                # 写入总数
                f.write(f"Total info count: {len(data)}\n")

                # 初始化问题字符串
                q = (
                    "你现在是一个冷静的文字分析大师！正在分析很多人的押注信息，并尝试回答一些问题。\n"
                    "请你根据下面这段文字总结出每一个人(每个人之间有多个-做分割)的押注结果！其中蓝等价右，红等价左！"
                    "注意：你只需要回答：名字--结果(左/右以红/蓝代替),格式为: 名字--结果， 一个结果占一行，如果没有结果，则结果为未知。\n"
                    "\n\n"
                )

                # 遍历data，写入文件和构建q
                for info in data:
                    name = info.get("name")
                    content = info.get("content")
                    pt = info.get("publish_time")

                    # 写入文件
                    # f.write(f"{"sep".center(50, "=")}\nname:{name}\npublish_time:{pt}\ncontent:\n{content}\n")

                    # 添加到问题字符串
                    q += f"{'-'.center(50, '-')}\nname:{name}\npublish_time:{pt}\ncontent:\n{content}\n"
                f.write(f"{"sep".center(50, "=")}\nq:{q}")
                log.info(f"Successfully wrote {len(data)} info entries to {file_path}")
            log.info(f"Successfully get {len(data)} info entries")
        except Exception as e:
            log.error(f"Error writing to file {file_path}: {str(e)}")

        # ai回答
        a = self.ai.ask_ai(q)
        log.file(f"question:{q}\nAI回答: {a}")
        print(a)
        return a

    # 解析回答
    def parse_answer(self):
        try:
            red_list = []
            blue_list = []
            red = ["左", "红"]
            blue = ["右", "蓝"]
            unknown = ["未知", "不知道", "不清楚", "无"]
            answer = self.conc_text()
            if not answer:
                log.info("没有获取到回答")
                return
            for line in answer.split("\n"):
                if not line:
                    continue
                name, res = line.split("--")
                if res.strip() in red:
                    red_list.append(name)
                elif res.strip() in blue:
                    blue_list.append(name)
                elif res.strip() in unknown:
                    continue
                else:
                    log.info(f"{name}结果解析失败: {res}")
            log.info(f"压红名单: {red_list}")
            log.info(f"压蓝名单: {blue_list}")
            log.info(f"总结目前:压红: {len(red_list)}, 压蓝: {len(blue_list)}")
            if not self.check_time():
                last_bet_time = self.str_to_time(self.config_data["last_bet"]["time"])
                # 如果上次押注时间距离现在小于2小时
                if (datetime.now() - last_bet_time).total_seconds() > 6900:  # 2小时
                    self.config_data["last_bet"] = {"time": self.time_to_str(datetime.now()), "red_up_list": red_list, "blue_up_list": blue_list}
                    self.write_config()
                    log.info("已更新上次上次押注时间及列表")
                else:
                    log.info(f"距离上次记录的押注时间不足2小时，上次押注时间为: {last_bet_time}")

            return "red" if len(red_list) >= len(blue_list) else "blue"  # self.state_finnal_result(red_list, blue_list)
        except Exception as e:
            log.error(f"解析回答失败: {str(e)}")

    def state_finnal_result(self, red_list: list[str], blue_list: list[str]):
        """
        计算红蓝双方的加权平均胜率，并选择胜率较高的一方作为最终押注结果。

        参数：
            red_list (list[str])  - 押注红方的玩家名称列表
            blue_list (list[str]) - 押注蓝方的玩家名称列表

        计算逻辑：
            1. 仅考虑胜率 ≥ 50% 的玩家（低于 50% 的玩家不会计入）。
            2. 计算加权平均胜率，权重使用“胜率平方”来增强高胜率玩家的影响：
            加权胜率 = (胜率²的总和) / (胜率的总和)
            3. 比较红蓝胜率，选择胜率较高的一方。

        返回：
            "red"  - 选择红方作为押注
            "blue" - 选择蓝方作为押注
            None   - 计算失败（例如输入为空）
        """
        try:
            if not red_list and not blue_list:
                raise ValueError("红蓝列表都为空，无法判断计算结果")

            # 计算红蓝的加权胜率
            red_weighted_sum = sum(self.rate.get(name, 0) * self.rate.get(name, 0) for name in red_list if self.rate.get(name, 0) >= 0.5)
            blue_weighted_sum = sum(self.rate.get(name, 0) * self.rate.get(name, 0) for name in blue_list if self.rate.get(name, 0) >= 0.5)

            # 计算权重总和（避免 0 除）
            red_weight_sum = sum(self.rate.get(name, 0) for name in red_list if self.rate.get(name, 0) >= 0.5)
            blue_weight_sum = sum(self.rate.get(name, 0) for name in blue_list if self.rate.get(name, 0) >= 0.5)

            # 计算加权平均胜率
            average_red_rate = red_weighted_sum / red_weight_sum if red_weight_sum > 0 else 0
            average_blue_rate = blue_weighted_sum / blue_weight_sum if blue_weight_sum > 0 else 0

            log.info(f"加权压红率: {average_red_rate:.2f}, 加权压蓝率: {average_blue_rate:.2f}")

            # 根据加权平均胜率判断结果
            if average_red_rate >= average_blue_rate:
                log.info(f"目前压红: {len(red_list)}, 压蓝: {len(blue_list)}, 加权压红率: {average_red_rate:.2f}, 加权压蓝率: {average_blue_rate:.2f}, 结果: 压红")
                return "red"
            else:
                log.info(f"目前压红: {len(red_list)}, 压蓝: {len(blue_list)}, 加权压红率: {average_red_rate:.2f}, 加权压蓝率: {average_blue_rate:.2f}, 结果: 压蓝")
                return "blue"

        except Exception as e:
            log.error(f"计算结果失败: {str(e)}")
            return None


if __name__ == "__main__":
    frog = Frog()
    frog.conc_text()
