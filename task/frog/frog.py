from task.based.Mytool.Click import Click
from task.based.Mytool.imageRec import ImageRec
from task.frog.spider_info import DynamicCollector
from PIGEON.reqai import ReqAI
import asyncio
from datetime import datetime, timedelta
from PIGEON.log import log
from time import sleep
from task.frog.res.img_info_auto_create import *


class Frog:
    def __init__(self, **kwargs):
        self.click = Click()
        self.image_rec = ImageRec()
        self.ai = ReqAI()
        self.uilist = [bet_lose, bet_win, frog, bet_on_confirm, bet_on, bet_done, bet_hall]
        self.task_switch = True
        self.running = kwargs.get("STOPSIGNAL", None)
        self.ui_delay = 0.5
        self.finnal_result = self.parse_answer()

    def calculate_time_to_10minutes_before_next_interval():
        """
        计算当前时间到下一个10分钟间隔结束前10分钟的剩余时间。

        该函数通过计算当前小时，确定下一个10分钟间隔的结束小时，并确保该小时在合理范围内（0-24）。
        如果结束小时超过24，则将其设置为第二天的0点。随后，计算在结束时间之前10分钟的时间点，
        并从当前时间到该时间点的剩余时间。

        返回格式为'hh:mm:ss'的字符串，表示剩余时间。如果剩余时间为负数或零，则返回'00:00:00'。

        Parameters:
            无

        Returns:
            str: 剩余时间，格式为'hh:mm:ss'，两位数表示小时、分钟和秒。

        Examples:
            >>> calculate_time_to_10minutes_before_next_interval()
            '01:10:00'
        """
        now = datetime.now()
        hour = now.hour

        # 计算结束小时
        end_hour = ((hour // 2) * 2) + 4

        # 确保end_hour不超过24
        if end_hour > 24:
            end_hour = 24

        # 创建结束时间
        if end_hour == 24:
            # 如果end_hour为24，则设置为第二天的0:00
            end_time = datetime(now.year, now.month, now.day + 1, 0, 0, 0)
        else:
            # 否则，设置为当天的end_hour点
            end_time = datetime(now.year, now.month, now.day, end_hour, 0, 0)

        # 计算区间结束前10分钟的时间点
        ten_minutes_before = end_time - timedelta(minutes=10)

        # 计算时间差
        time_diff = ten_minutes_before - now

        # 如果时间差为负数，返回"00:00:00"
        if time_diff.total_seconds() <= 0:
            return "00:00:00"

        # 将时间差转换为h:m:s格式
        total_seconds = time_diff.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        # 格式化输出
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def check_time(self):
        now = datetime.now()
        current_hour = now.hour
        today_10am = datetime(now.year, now.month, now.day, 10)

        # 如果当前时间在10点前，计算到当天11:40的时间差
        if now < today_10am:
            target_time = today_10am.replace(hour=11, minute=50, second=0)
            delta = target_time - now
        else:
            # 处理活动时间内（10:00-24:00）的逻辑
            start_h = (current_hour // 2) * 2
            # 确保起始小时不小于10
            if start_h < 10:
                start_h = 10

            # 计算当前区间的结束时间（处理跨天）
            end_h = start_h + 2
            days_add_end, end_h = divmod(end_h, 24)
            end_time = datetime(now.year, now.month, now.day) + timedelta(days=days_add_end, hours=end_h)

            # 当前区间的最后20分钟开始时间
            start_last_20min = end_time - timedelta(minutes=10)

            if start_last_20min <= now < end_time:
                return False
            else:
                # 不在最后20分钟内，计算到当前区间最后20分钟的时间差
                if now < start_last_20min:
                    delta = start_last_20min - now
                else:
                    # 当前时间超过当前区间，直接返回0（理论上不会发生）
                    delta = timedelta(0)

        # 格式化时间差为HH:MM:SS
        total_seconds = delta.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def set_parms(self, **kwargs):
        self.ui_delay = float(kwargs.get("ui_delay", 1))

    def loop(self):
        if time_delta := self.check_time():
            log.info(f"距离下一轮押注还有{time_delta} ")
            self.next_time = time_delta
            return
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

    def run(self):
        sleep(self.ui_delay)
        res = self.image_rec.match_ui(self.uilist)
        log.insert("2.1", f"UI match: {res} ")
        match res:
            case "bet_done":
                self.next_time = self.calculate_time_to_10minutes_before_next_interval()
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
                # 获取决定下注的位置, 并点击
                if self.finnal_result == "red":
                    self.click.area_click(left[1])
                elif self.finnal_result == "blue":
                    self.click.area_click(right[1])
                else:
                    log.info("未知结果")
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
                    log.info("确认下注")
                else:
                    log.info("未知结果")
                # 点击确认
        pass

    async def get_info(self):
        # 自定义UID映射（可选）
        custom_uids = {
            "d9dc2a75497c4a91b2db1e909a36544d": "查查尔",
            "b6b5bc8277e34f69aeca018db0081397": "林木不是森",
            "3d4726d99f2642a485729695b798cb8c": "梅布斯尼",
            "c3c989fae4074d04b478b8ba47ae4120": "徐OK",
            "462382f1127b46c5add1185d88f0ea40": "面灵气喵",
            "aaa923436aa440df9ac1ee3f47387b99": "雯雯、",
            "1d2dcbbd7e3d481c8d0f27ba4ff0dc71": "鸽海程璐",
            "8982241de1844638b4bb455139b8dcc0": " 丶不知名清流",
            "fbdbd850d87f42768440468199790e3f": "流沙河底",
            "840742d60e4a43208605ae68ca8c3f64": "七面相",
            "30e383c884f844a18a7a76fe3c1e888f": "天真·珈百璃",
            "74adeb1bfb2b4cf382edbbb430da2149": "安掌门",
            "21657a558bdd4ddfb6501298350336e7": "徐清林",
            "74adeb1bfb2b4cf382edbbb430da2149": "prince班奇",
            "72584a679e2f45b6859566b5523400d5": "晨时微凉",
            "e7107cd3010e418da26672669d8eeb5e": "嘤嘤井",
            "54399446d5084a0e8878dac8f6ff56d0": "余岁岁",
            "e87f855f36f24b34b9d8f8a4fb2d62b2": "yys靠脸混饭",
            "82de68c7672e4b6da65493fb829b57b6": "夜神月丶L",
        }

        async with DynamicCollector(uid_mapping=custom_uids) as collector:
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
                    "你现在是一个文字分析大师！正在分析很多人的押注信息，并尝试回答一些问题。"
                    "请你根据下面这段文字总结出每一个人(每个人之间有多个-做分割)压蓝or红，蓝等价右，红等价左！"
                    "只需要回答结果(左/右以红/蓝代替),格式为: 名字--结果， 一个结果占一行。遵循以下的规则："
                    "1、如果没有明确的结果倾向，则回复未知；"
                    "2、如果content中有提到这是一个55开的对局，或者是一个较难判断的对局，即两边机会均等，则将他的结果设置为押注红方。"
                    "\n\n"
                )

                # 遍历data，写入文件和构建q
                for info in data:
                    name = info.get("name")
                    content = info.get("content")
                    pt = info.get("publish_time")

                    # 写入文件
                    f.write(f"{"sep".center(50, "=")}\nname:{name}\npublish_time:{pt}\ncontent:\n{content}\n")

                    # 添加到问题字符串
                    q += f"{'分割线'.center(50, '-')}\nname:{name}\npublish_time:{pt}\ncontent:\n{content}\n"

                log.info(f"Successfully wrote {len(data)} info entries to {file_path}")
            log.info(f"Successfully get {len(data)} info entries")
        except Exception as e:
            log.error(f"Error writing to file {file_path}: {str(e)}")

        # ai回答
        a = self.ai.ask_ai(q)
        return a

    # 解析回答
    def parse_answer(self):
        red_list = []
        blue_list = []
        red = ["左", "红"]
        blue = ["右", "蓝"]
        unknown = ["未知", "不知道", "不清楚"]
        answer = self.conc_text()
        if not answer:
            log.info("没有获取到回答")
            return
        for line in answer.split("\n"):
            if not line:
                continue
            name, res = line.split("--")
            if res in red:
                red_list.append(name)
            elif res in blue:
                blue_list.append(name)
            elif res in unknown:
                continue
            else:
                log.info(f"结果解析失败: {res}")
        log.info(f"压红名单: {red_list}")
        log.info(f"压蓝名单: {blue_list}")
        log.info(f"总结目前:压红: {len(red_list)}, 压蓝: {len(blue_list)}")
        return "red" if len(red_list) > len(blue_list) else "blue"


if __name__ == "__main__":
    frog = Frog()
    frog.conc_text()
