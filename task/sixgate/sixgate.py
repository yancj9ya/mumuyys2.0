# 六道之门
from task.based.Mytool.Click import Click
from task.based.Mytool.imageRec import ImageRec
from task.based.Mytool.Ocr import Ocr
from task.based.Mytool.Counter import Counter
from task.based.base.res.base_img import *
from task.sixgate.res.img_info_auto_create import *
from time import sleep, time, strftime, localtime
from PIGEON.log import Log
from random import shuffle
from win11toast import toast

log = Log()


class SixGate(Click, ImageRec):
    def __init__(self, **kwargs):
        Click.__init__(self)
        ImageRec.__init__(self)

        self.ocr = Ocr()
        self.switch = True

        self.running = kwargs.get("STOPSIGNAL", None)
        self.uilist = [
            sg_open,
            call_store_confirm,
            event_chose_page,
            event_ezbattle_page,  # 鏖战
            event_chaos_page,  # 混沌
            event_secret_page,  # 神秘
            event_store_page,  # 商店
            event_skip_page,  # 绽放之宇
            battle_end_reward_chose,  # 战斗结束奖励选择
            chose_buff_confirm,  # 选择buff确认
            need_click_blank,  # 点击空白跳过
            final_boss,  # 最终boss
            final_award,  # 最终奖励
            team_confirm1,  # 队伍确认1
            team_confirm2,  # 队伍确认2
            init_buff_chose,  # 初始buff选择
            init_skill_chose,  # 初始技能选择
            full_buff,  # buff等级满了
        ]
        self.ui_delay = 0.5
        self.challenge_count = Counter("challenge_count")

        self.buff_level = Counter("buff_level")  # 初始buff等级
        self.skill_level = Counter("skill_level")  # 初始技能等级
        self.step_count = Counter("step_count")  # 关卡数
        self.challenge_count = Counter("challenge_count")  # 挑战次数

    def set_parms(self, **kwargs):
        self.times = int(kwargs.get("times", 0))
        self.ui_delay = kwargs.get("ui_delay", 0.5)

    def loop(self):
        log.info(f"{'六道之门开始运行':*^22}")
        if self.times == 0:
            log.error("times参数为0，退出运行")
        while self.switch:
            match self.running.state:
                case "RUNNING":
                    self.run()
                case "STOP":
                    return
                case "WAIT":
                    sleep(1)
                    continue
                case _:
                    pass
        pass

    def run(self):
        sleep(self.ui_delay)
        match_result = self.match_ui(self.uilist)
        log.insert("2.1", f"Matched UI:{match_result}")
        match match_result:
            case "call_store_confirm":
                self.area_click(call_store_confirm[1])
            case "event_chose_page":
                self.event_chose_page()
            case "event_ezbattle_page":
                self.event_ezbattle_page()
            case "event_chaos_page":
                self.event_chaos_page()
            case "event_secret_page":
                self.event_secret_page()
            case "event_store_page":
                self.event_store_page()
            case "event_skip_page":
                self.event_skip_page()
            case "need_click_blank":
                self.need_click_blank()
            case "battle_end_reward_chose" | "chose_buff_confirm":
                self.battle_end_reward_chose()
            case "final_boss":
                self.final_boss()
            case "final_award":
                self.final_award()
            case "sg_open":
                self.sg_open()
            case "init_buff_chose":
                self.init_buff_chose()
            case "init_skill_chose":
                self.init_skill_chose()
            case "team_confirm1":
                self.team_confirm1()
            case "team_confirm2":
                self.team_confirm2()
            case _:
                log.insert("2.2", f"No matched UI:{match_result}")
                log.insert("3.0", f"Current coin: {self.coin_num if hasattr(self, 'coin_num') else 'unknown'}")
                log.insert("4.0", f"Buff level: {self.buff_level.count},Skill level: {self.skill_level.count},Step count: {self.step_count.count}")
        pass

    def dyn_event_priority(self):
        """
        根据 buff_level 动态生成事件优先级列表。

        :return: 事件优先级列表
        """
        if (self.buff_level.count > 4 or self.step_count.count >= 10) and self.skill_level.count >= 1:
            return ["event_secret", "event_store", "event_chaos", "event_ezbattle"]
        elif self.buff_level.count > 4 and self.skill_level.count < 1:
            return ["event_store", "event_secret", "event_chaos", "event_ezbattle"]
        else:
            return ["event_ezbattle", "event_chaos", "event_secret", "event_store"]

    def event_sort(self, event_dict: dict):
        """
        根据动态优先级对事件字典进行排序。

        :param event_dict: 事件字典，键为事件名称，值为事件数据
        :return: 排序后的事件字典
        """
        # 类型检查
        if not isinstance(event_dict, dict):
            raise TypeError("event_dict 必须是一个字典")
        # 动态生成优先级列表
        reference = {words: idx for idx, words in enumerate(self.dyn_event_priority())}
        # 按优先级排序
        sorted_items = sorted(event_dict.items(), key=lambda x: reference.get(x[0], float("inf")))
        # 返回最高优先级的事件
        return sorted_items[0]

    def get_step(self):
        """
        获取当前的关卡数。

        :return: 当前的关卡数
        """
        return self.step_count.count
        pass

    def get_coin_num(self):
        """
        获取当前的金币数量。

        :return: 当前的金币数量
        """
        if self.match_img(prepare_battle_btn):
            self.area_click(prepare_battle_btn[1])
            sleep(0.5)
        if self.match_img(prepare_battle):
            _coin = self.ocr.ocr_by_re((1146, 30, 1220, 57), r"\d+")[0]
            self.area_click((21, 23, 52, 57))
            log.info(f"<prepare>:Current coin: {_coin}")
            return int(_coin)
        pass

    def update_award_coin(self):
        """
        更新金币数量，在战斗选择奖励的界面中调用。

        :return: coin数量
        """
        ocr_res = self.ocr.ocr_by_re((1155, 22, 1238, 52), r"\d+")
        if ocr_res:
            _coin = int(ocr_res[0])
            log.info(f"<award>:Current coin: {_coin}")
            log.insert("3.0", f"Current coin: {_coin}")
            return _coin

    def call_store(self):
        """
        召唤商店购买。

        :return: None
        """
        if self.match_img(call_store):
            self.area_click(call_store[1])
            sleep(0.5)
        if self.match_img(call_store_confirm):
            self.area_click(call_store_confirm[1])
            log.info("<store>:call store")
            self.coin_num -= 300
            log.insert("3.0", f"Current coin: {self.coin_num}")

        else:
            log.info("<store>:No call store confirm btn")
            return False

        pass

    def event_chose_page(self):
        """事件选择界面"""
        # 金币不足仍然进入商店
        if self.match_img(not_enough_coin):
            self.area_click(not_enough_coin[1])
        # 更新一下关卡数
        if self.get_step() == 0:
            if ocr_res := self.ocr.ocr_by_re((1065, 233, 1094, 256), r"\d+"):
                self.step_count.count = 20 - int(ocr_res[0])

        # 生成事件列表
        event_list = [event_ezbattle, event_chaos, event_secret, event_store, event_skip]

        # 找到界面上存在的事件
        available_events = self.find_duo_img(event_list, (51, 89, 1249, 650))
        log.file(f"Available events: {available_events}")

        # 按动态的优先级排序
        if not available_events:
            log.insert("2.3", "No event found")
            return
        else:
            # 按动态的优先级排序
            available_events_tuple = self.event_sort(available_events)
            log.insert("5.0", f"Events: {available_events_tuple[0]}")

        # 构造多个条件判断
        # 1.coin条件
        coin_300 = hasattr(self, "coin_num") and self.coin_num is not None and self.coin_num >= 300
        coin_500 = hasattr(self, "coin_num") and self.coin_num is not None and self.coin_num >= 500
        # 2.skill条件
        skill_1 = self.skill_level.count > 1
        # 3.step条件
        step_10 = self.get_step() >= 10
        # 4.event 可跳过类型条件
        skip_able_event = available_events_tuple[0] in ["event_store", " event_skip", "event_secret"]
        # 5.出现4个event 不可call store
        event_four = len(available_events) == 4
        # 6.buff等级不够5级
        buff_level_5 = self.buff_level.count < 5

        # 出现4个event 直接执行事件
        if event_four:
            log.info(f"event_four: normal run")
            self.area_click(available_events_tuple[1])
            # 关卡数+1
            self.step_count.increment(interval=1.5)
            return

        # buff等级不够5级，直接执行
        if buff_level_5:
            log.info(f"buff_level<5, normal run")
            self.area_click(available_events_tuple[1])
            # 关卡数+1
            self.step_count.increment(interval=1.5)
            return

        log.debug(f"{coin_300, coin_500, skill_1, step_10, skip_able_event}")
        match (coin_300, coin_500, skill_1, step_10, skip_able_event):
            # 金币条件为false，则都不考虑
            case (False, _, _, _, _):
                log.info(f"coin<300, normal run")
                self.area_click(available_events_tuple[1])
                # 关卡数+1
                self.step_count.increment(interval=1.5)
                return
            # 在step<10时，不考虑快速跳过
            case (_, _, _, False, _):
                log.info(f"step<10, normal run")
                self.area_click(available_events_tuple[1])
                # 关卡数+1
                self.step_count.increment(interval=1.5)
                return
            # 可跳过事件，且技能大于1，则直接执行
            case (_, _, True, _, True):
                log.info(f"skill>1 and event skipable, Skip event")
                self.area_click(available_events_tuple[1])
                # 关卡数+1
                self.step_count.increment(interval=1.5)
                return
            # 技能小于1，但金币够500购买,step大于10,不可跳过事件
            case (_, True, False, True, False):
                log.info(f"skill<1 and coin>500 and step>10, Call store")
                self.call_store()
                return
            # 技能大于1，且金币够300，step大于10,不可跳过类型事件
            case (True, _, True, True, False):
                log.info(f"skill>1 and coin>300 and step>10, call store")
                self.call_store()
                return
            # 技能小于1，金币不够300，step大于10,不可跳过类型事件
            case (False, _, False, True, False):
                log.info(f"skill<1 and coin<300 and step>10, normal run")
                self.area_click(available_events_tuple[1])
            case _:
                log.info(f"No matched condition, normal run")
                log.debug(f"{coin_300, coin_500, skill_1, step_10, skip_able_event}")
                self.area_click(available_events_tuple[1])

    def event_ezbattle_page(self):
        """鏖战界面"""
        # 点击右侧的技能挑战对象
        self.area_click(event_ezbattle_skill[1])
        # 确认挑战
        if click_obj := self.match_img(event_ezbattle_challenge):
            self.area_click(click_obj)

    def event_chaos_page(self):
        """混沌界面"""
        # 通过识别退出按钮判断是宝箱类型还是战斗类型
        if self.match_img(event_chaos_page_exit):
            # 点击退出按钮
            self.area_click(event_chaos_page_exit[1], animation_time=0.5)
        else:
            # 战斗类型，点击挑战对象
            self.area_click(event_chaos_skill[1])
            # 确认挑战
            if click_obj := self.match_img(event_ezbattle_challenge):
                self.area_click(click_obj)
        pass

    def event_secret_page(self):
        """神秘界面"""
        # 神秘界面直接退出
        if click_obj := self.match_img(
            event_secret_page_exit,
        ):
            self.area_click(click_obj, animation_time=0.5)

    def event_store_page(self):
        """商店界面"""
        if self.match_img(event_store_page_exit):  # 页面加载完毕
            # 先获取金币数量
            if ocr_res := self.ocr.ocr_by_re((1157, 21, 1239, 54), r"\d+"):
                self.coin_num = int(ocr_res[0])
        else:  # 页面未加载完毕
            return
        log.info(f"<store>:Current coin: {self.coin_num}")
        # 判断是否需要购买
        if self.coin_num >= 200 and self.skill_level.count < 1:
            # sleep(2)
            for _ in range(3):
                # 点击购买按钮
                if click_obj := self.match_img(buy_store_thunder, accuracy=0.8):  # 特殊处理，最后一个部分区域点击不动
                    x1, y1, x2, y2 = click_obj
                    if 1032 <= (x1 + x2) / 2 <= 1161 and 662 <= (y1 + y2) / 2 <= 699:
                        # 条件成立时执行的代码:
                        self.area_click((1029, 592, 1043, 666))
                    else:
                        self.area_click(click_obj)
                    sleep(1)
                    log.info("<store>:Buying Thunder in Store")
                else:
                    # 在coin>=300的情况下，如果没有找到对应技能，则刷新商店
                    # 刷新商店，一次-100
                    if self.coin_num >= 300:
                        self.area_click((595, 599, 633, 638))  # 点击刷新按钮
                        self.coin_num -= 100  # 刷新一次扣100
                        sleep(1)
                        log.info("<store>:Refreshing Store")
                    else:
                        break

                if click_obj := self.match_img(buy_store_thunder_confirm):
                    self.area_click(click_obj)
                    self.coin_num -= 300
                    self.skill_level.increment()
                    log.insert("4.0", f"Buff level: {self.buff_level.count},Skill level: {self.skill_level.count}")
                    return
        else:
            # 点击退出按钮
            if click_obj := self.match_img(event_store_page_exit):
                self.area_click(click_obj, animation_time=0.5)
        # 先判断无确认购买按钮，防止没有购买就退出
        if not self.match_img(buy_store_thunder_confirm):
            # 点击退出按钮
            if click_obj := self.match_img(event_store_page_exit):
                self.area_click(click_obj, animation_time=0.5)

    def event_skip_page(self):
        """绽放之宇界面"""
        # 不打，直接跳过
        if click_obj := self.match_img(event_skip_page_exit):
            self.area_click(click_obj, animation_time=1)

    def battle_end_reward_chose(self):
        """战斗结束奖励选择"""
        # 更新一下coin_num
        if res := self.update_award_coin():
            self.coin_num = res
        # 先判断左侧有无需要的技能,有则选择
        if position := self.match_img(sg_skill_thunder):
            x1, y1, x2, y2 = position
            chose_position = (x1, y1 + 274, x2, y2 + 274)
            self.area_click(chose_position)
            self.skill_level.increment()
            log.insert("4.0", f"Buff level: {self.buff_level.count},Skill level: {self.skill_level.count}")
        else:
            # 无需要的技能，则强化舞技力量
            x1, y1, x2, y2 = battle_end_reward_chose[1]
            chose_position = (x1, y1 + 274, x2, y2 + 274)
            self.area_click(chose_position, animation_time=0.5)

            # 点击确认
            if click_obj := self.match_img(chose_buff_confirm):
                # 更新一下buff_level
                if self.buff_level.count == 0:
                    if ocr_res := self.ocr.ocr_by_re((250, 235, 276, 259), r"\d+"):
                        self.buff_level.count = int(ocr_res[0])
                self.area_click(click_obj)
                self.buff_level.increment(2)
                log.insert("4.0", f"Buff level: {self.buff_level.count},Skill level: {self.skill_level.count}")
            elif self.match_img(full_buff):
                self.buff_level.count = 10
                log.insert("4.0", f"Buff level: {self.buff_level.count},Skill level: {self.skill_level.count}")
                self.area_click((780, 504, 869, 534))

    def need_click_blank(self):
        """点击空白跳过"""
        self.area_click(need_click_blank[1])

    def final_boss(self):
        """最终boss"""
        # 点击挑战按钮即可
        self.area_click((1128, 603, 1195, 669))
        sleep(0.5)
        # 清除buff skill coin
        self.buff_level.reset()
        self.skill_level.reset()
        self.step_count.reset()
        if hasattr(self, "coin_num"):
            del self.coin_num
        self.challenge_count.increment()
        log.debug(f"<challenge>:Challenge count: {self.challenge_count.count}")
        if self.challenge_count.count >= self.times:
            self.switch = False

    def final_award(self):
        """使用双倍奖励"""
        # 如果弹出双倍使用奖励的提示框，点击确认
        if click_obj := self.match_img(use_double_reward_confirm):
            self.area_click(click_obj)
        else:
            # 点击下方空白处跳过奖励
            self.area_click((580, 564, 825, 641))

        pass

    def sg_open(self):
        """开始界面"""
        # 点击开启按钮
        self.area_click(sg_open[1])

    def team_confirm1(self):
        """队伍确认1"""
        # 点击确认
        self.area_click(team_confirm1[1])

    def team_confirm2(self):
        """队伍确认2"""
        # 点击确认
        self.area_click(team_confirm2[1])

    def init_buff_chose(self):
        """初始buff选择"""
        self.area_click(init_buff_chose_btn[1])

    def init_skill_chose(self):
        """初始技能选择"""
        self.area_click(init_skill_chose_btn[1])
