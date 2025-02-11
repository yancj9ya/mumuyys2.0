# -*- coding: utf-8 -*-
from collections import namedtuple
from page.switcher import Page, JumpAction, PageNavigator


class IMG:
    BOARD = ["page/res/BOARD.bmp", (12, 398, 521, 440), "BOARD"]  # (7, 345, 285, 461)
    FENGMO = ["page/res/fengmo.bmp", (355, 148, 955, 596), "FENGMO"]
    SHADOW_GATE_TEXT = ["page/res/SHADOW_GATE_TEXT.bmp", (355, 148, 955, 596), "SHADOW_GATE"]

    # 通过庭中的跳转,暂时使用不到
    # step_BACK_street = ["tool/switchui/res/step_BACK_street.bmp", [575, 349, 599, 398], "step_BACK_street"]
    # step_BACK_street_1 = ["tool/switchui/res/step_BACK_street_1.bmp", [688, 322, 718, 370], "step_BACK_street_1"]
    # step_BACK_street_2 = ["tool/switchui/res/step_BACK_street_2.bmp", [717, 320, 743, 373], "step_BACK_street_2"]
    # step_BACK_street_3 = ["tool/switchui/res/step_BACK_street_3.bmp", [836, 238, 866, 280], "step_BACK_street_3"]
    # # 庭院到町中
    # HOME_PAGEUNFOLD_TO_BACKSTREET = {
    #     "HOME_PAGEUNFOLD_TO_BACKSTREET1": step_BACK_street,
    #     "HOME_PAGEUNFOLD_TO_BACKSTREET2": step_BACK_street_1,
    #     "HOME_PAGEUNFOLD_TO_BACKSTREET3": step_BACK_street_2,
    #     "HOME_PAGEUNFOLD_TO_BACKSTREET4": step_BACK_street_3,
    # }

    # 庭院到探索
    step_ts = ["tool/switchui/res/step_ts.bmp", [487, 169, 516, 196], "step_ts"]
    step_ts_1 = ["tool/switchui/res/step_ts_1.bmp", [457, 182, 483, 206], "step_ts_1"]
    step_ts_2 = ["tool/switchui/res/step_ts_2.bmp", [547, 147, 573, 173], "step_ts_2"]
    step_ts_3 = ["tool/switchui/res/step_ts_3.bmp", (164, 258, 798, 303), "step_ts_3"]  # (164, 258,798, 303)

    HOME_PAGEUNFOLD_TO_TS = {
        "HOME_PAGEUNFOLD_TO_TS1": step_ts,
        "HOME_PAGEUNFOLD_TO_TS2": step_ts_1,
        "HOME_PAGEUNFOLD_TO_TS3": step_ts_2,
        "HOME_PAGEUNFOLD_TO_TS4": step_ts_3,
    }

    # 返回的识图样式
    BACK = ["tool/switchui/res/step_BACK.bmp", (11, 12, 183, 209), "step_BACK"]
    BACK_2 = ["tool/switchui/res/step_BACK_2.bmp", (11, 12, 183, 209), "step_BACK_2"]
    BACK_3 = ["tool/switchui/res/step_BACK_3.bmp", (11, 12, 183, 209), "step_BACK_3"]

    BACK = {"BACK1": BACK, "BACK2": BACK_2, "BACK3": BACK_3}


# ========== 初始化配置 ========== #
# 创建页面导航实例
nav = PageNavigator(timeout=30, retry=5, cooldown=1)

# 定义页面
EXPLORE = Page("EXPLORE", ["page/res/EXPLORE.bmp", [1136, 123, 1176, 165], "EXPLORE"])
HARD_28 = Page("HARD_28", ["page/res/HARD_28.bmp", [1082, 253, 1111, 320], "HARD_28"])
COMBAT_28 = Page("COMBAT_28", ["page/res/COMBAT_28.bmp", [156, 654, 253, 688], "COMBAT_28"])
ENCHANTMENT_1 = Page("ENCHANTMENT_1", ["page/res/ENCHANTMENT_1.bmp", [39, 448, 107, 491], "ENCHANTMENT_1"])
ENCHANTMENT_2 = Page("ENCHANTMENT_2", ["page/res/ENCHANTMENT_2.bmp", [240, 603, 304, 630], "ENCHANTMENT_2"])
REGIONAL_DEMON_KING = Page("REGIONAL_DEMON_KING", ["page/res/REGIONAL_DEMON_KING.bmp", [50, 371, 86, 425], "REGIONAL_DEMON_KING"])
COURTYARD_FOLD = Page("COURTYARD_FOLD", ["page/res/COURTYARD_FOLD.bmp", [54, 625, 89, 659], "COURTYARD_FOLD"])
COURTYARD_UF = Page("COURTYARD_UF", ["page/res/COURTYARD_UF.bmp", [493, 13, 526, 50], "COURTYARD_UF"])
YY_SHACK = Page("YY_SHACK", ["page/res/YY_SHACK.bmp", [1173, 616, 1239, 669], "YY_SHACK"])
SHRINE = Page("SHRINE", ["page/res/SHRINE.bmp", [1184, 379, 1212, 450], "SHRINE"])
TEMPLE_CHOSE = Page("TEMPLE_CHOSE", ["page/res/TEMPLE_CHOSE.bmp", [98, 32, 227, 72], "TEMPLE_CHOSE"])
SHIKI_RECORD = Page("SHIKI_RECORD", ["page/res/SHIKI_RECORD.bmp", [94, 20, 198, 65], "SHIKI_RECORD"])
WARD = Page("WARD", ["page/res/WARD.bmp", (232, 401, 334, 515), "WARD"])
SOUL_PET = Page("SOUL_PET", ["page/res/SOUL_PET.bmp", [108, 22, 172, 63], "SOUL_PET"])
BOARD_ACTIVITY = Page("BOARD_ACTIVITY", ["page/res/BOARD_ACTIVITY.bmp", [604, 66, 673, 104], "BOARD_ACTIVITY"])
BOARD_DAILY = Page("BOARD_DAILY", ["page/res/BOARD_DAILY.bmp", [605, 65, 671, 103], "BOARD_DAILY"])
BOSS_DAILY = Page("BOSS_DAILY", ["page/res/BOSS_DAILY.bmp", [1114, 691, 1158, 714], "BOSS_DAILY"])
SHADOW_GATE = Page("SHADOW_GATE", ["page/res/SHADOW_GATE.bmp", [1087, 612, 1139, 669], "SHADOW_GATE"])
SERVER = Page("SERVER", ["page/res/SERVER.bmp", (13, 371, 374, 684), "SERVER"])

# 定义跳转逻辑
# 选择服务器-庭院
SERVER.add_action("选择服务器-庭院", JumpAction.CLICK_TYPE, (578, 587, 699, 609), COURTYARD_FOLD)

# 结界突破跳转
ENCHANTMENT_1.add_action("结界突破-探索", JumpAction.XCLICK_TYPE, (1192, 119, 1228, 154), EXPLORE)
ENCHANTMENT_1.add_action("结界突破-寮突破", JumpAction.CLICK_TYPE, (1214, 374, 1247, 444), ENCHANTMENT_2)
ENCHANTMENT_1.add_action("结界突破-式神录", JumpAction.CLICK_TYPE, (1218, 620, 1247, 652), SHIKI_RECORD)

# 寮突破跳转
ENCHANTMENT_2.add_action("寮突破-结界突破", JumpAction.CLICK_TYPE, (1216, 249, 1248, 324), ENCHANTMENT_1)
ENCHANTMENT_2.add_action("寮突破-探索", JumpAction.XCLICK_TYPE, (1192, 119, 1228, 154), EXPLORE)
ENCHANTMENT_2.add_action("结界突破-式神录", JumpAction.CLICK_TYPE, (1218, 620, 1247, 652), SHIKI_RECORD)

# 庭院展开跳转
COURTYARD_UF.add_action("庭院展开-地藏像", JumpAction.IMAGE_TYPE, IMG.BOARD, BOARD_ACTIVITY)
COURTYARD_UF.add_action("庭院展开-探索", JumpAction.IMAGE_TYPE, IMG.HOME_PAGEUNFOLD_TO_TS, EXPLORE)
COURTYARD_UF.add_action("庭院展开-式神录", JumpAction.CLICK_TYPE, (1129, 628, 1162, 659), SHIKI_RECORD)
COURTYARD_UF.add_action("庭院展开-阴阳寮", JumpAction.CLICK_TYPE, (567, 620, 595, 656), YY_SHACK)

# 庭院收缩跳转
COURTYARD_FOLD.add_action("庭院展开-探索", JumpAction.IMAGE_TYPE, IMG.HOME_PAGEUNFOLD_TO_TS, EXPLORE)
COURTYARD_FOLD.add_action("庭院收缩-庭院展开", JumpAction.CLICK_TYPE, (1199, 631, 1240, 686), COURTYARD_UF)

# 神社跳转
SHRINE.add_action("神社-道馆", JumpAction.CLICK_TYPE, (478, 212, 544, 262), TEMPLE_CHOSE)
SHRINE.add_action("神社-阴阳寮", JumpAction.XCLICK_TYPE, (33, 16, 69, 48), YY_SHACK)

# 阴阳寮跳转
YY_SHACK.add_action("阴阳寮-庭院展开", JumpAction.CLICK_TYPE, (36, 22, 75, 63), COURTYARD_UF)
YY_SHACK.add_action("阴阳寮-神社", JumpAction.CLICK_TYPE, (883, 634, 925, 680), SHRINE)
YY_SHACK.add_action("阴阳寮-寄养", JumpAction.CLICK_TYPE, (1083, 638, 1112, 679), WARD)

# 探索跳转
EXPLORE.add_action("探索-困难挑战", JumpAction.CLICK_TYPE, (1084, 523, 1219, 569), HARD_28)
EXPLORE.add_action("探索-结界突破", JumpAction.CLICK_TYPE, (266, 648, 298, 678), ENCHANTMENT_1)
EXPLORE.add_action("探索-地域鬼王", JumpAction.CLICK_TYPE, (654, 644, 688, 682), REGIONAL_DEMON_KING)
EXPLORE.add_action("探索-契灵", JumpAction.CLICK_TYPE, (1047, 650, 1085, 683), SOUL_PET)
EXPLORE.add_action("探索-庭院", JumpAction.XCLICK_TYPE, (37, 41, 78, 81), COURTYARD_UF)


# 阴界返回
SHADOW_GATE.add_action("阴界-庭院", JumpAction.XCLICK_TYPE, (69, 44, 102, 82), COURTYARD_UF)
# 逢魔返回
BOSS_DAILY.add_action("逢魔-庭院", JumpAction.IMAGE_TYPE, IMG.BACK, COURTYARD_UF)
# 契灵返回
SOUL_PET.add_action("契灵-探索", JumpAction.XCLICK_TYPE, IMG.BACK, EXPLORE)
# 式神录返回
SHIKI_RECORD.add_action("式神录-庭院", JumpAction.XCLICK_TYPE, IMG.BACK, COURTYARD_UF)
# 道馆跳转
TEMPLE_CHOSE.add_action("道馆-神社", JumpAction.XCLICK_TYPE, IMG.BACK, SHRINE)
# 寄养跳转
WARD.add_action("寄养-阴阳寮", JumpAction.XCLICK_TYPE, (27, 27, 66, 65), YY_SHACK)
# 地鬼跳转
REGIONAL_DEMON_KING.add_action("地鬼-探索", JumpAction.XCLICK_TYPE, (58, 40, 86, 79), EXPLORE)
REGIONAL_DEMON_KING.add_action("地鬼-式神录", JumpAction.CLICK_TYPE, (1198, 513, 1230, 548), SHIKI_RECORD)

# 地藏日常跳转
BOARD_DAILY.add_action("地藏像日常-逢魔", JumpAction.IMAGE_TYPE, IMG.FENGMO, BOSS_DAILY)
BOARD_DAILY.add_action("地藏像日常-阴界", JumpAction.IMAGE_TYPE, IMG.SHADOW_GATE_TEXT, SHADOW_GATE)

BOARD_DAILY.add_action("地藏日常-活动", JumpAction.CLICK_TYPE, (1109, 320, 1133, 407), BOARD_ACTIVITY)
BOARD_DAILY.add_action("地藏像-庭院", JumpAction.CLICK_TYPE, (1135, 80, 1164, 109), COURTYARD_UF)


# 地藏像活动跳转
BOARD_ACTIVITY.add_action("地藏像-庭院", JumpAction.CLICK_TYPE, (1135, 80, 1164, 109), COURTYARD_UF)
BOARD_ACTIVITY.add_action("地藏像-日常", JumpAction.CLICK_TYPE, (1104, 170, 1133, 250), BOARD_DAILY)

# 困难挑战跳转
HARD_28.add_action("困难挑战-探索", JumpAction.XCLICK_TYPE, (1035, 132, 1072, 174), EXPLORE)
HARD_28.add_action("困难跳转-副本战斗", JumpAction.CLICK_TYPE, (915, 522, 982, 561), COMBAT_28)

# 困28副本战斗跳转
COMBAT_28.add_action("副本战斗-困难挑战", JumpAction.CLICK_TYPE, [(35, 44, 77, 86), (738, 391, 817, 423)], HARD_28)


# 注册所有页面
nav.register_page(EXPLORE)
nav.register_page(COMBAT_28)
nav.register_page(HARD_28)
nav.register_page(ENCHANTMENT_1)
nav.register_page(ENCHANTMENT_2)
nav.register_page(COURTYARD_FOLD)
nav.register_page(COURTYARD_UF)
nav.register_page(YY_SHACK)
nav.register_page(WARD)
nav.register_page(SHRINE)
nav.register_page(TEMPLE_CHOSE)
nav.register_page(REGIONAL_DEMON_KING)
nav.register_page(SHIKI_RECORD)
nav.register_page(SOUL_PET)
nav.register_page(BOARD_ACTIVITY)
nav.register_page(BOARD_DAILY)
nav.register_page(BOSS_DAILY)
nav.register_page(SHADOW_GATE)
nav.register_page(SERVER)
