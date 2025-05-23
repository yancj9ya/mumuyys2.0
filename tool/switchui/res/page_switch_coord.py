# This file is used to store the coordinates of the switch page elements.
from task.based.switchui.res.img_info_auto_create import *

tp_main_TO_ts_main = (1189, 117, 1220, 150)

ts_main_TO_tp_main = (258, 645, 299, 676)
ts_main_TO_ts_tz = (1092, 514, 1204, 563)
ts_main_TO_area_demon = (650, 641, 697, 689)
ts_main_TO_home_page_unfold = (50, 43, 75, 75)

ts_tz_TO_ts_main = (1027, 133, 1069, 171)
ts_tz_TO_ts_cm = (895, 516, 990, 558)

ts_cm_TO_ts_tz = [(34, 42, 69, 81), (718, 389, 823, 415)]

tp_end_mark_TO_tp_main = (990, 462, 1125, 520)

ts_end_mark_TO_ts_cm = (990, 462, 1125, 520)

tp_damo_TO_tp_main = (560, 475, 662, 551)


home_page_fold_TO_home_page_unfold = (1217, 610, 1242, 674)

# 2024/12/8

area_demon_TO_ts_main = (58, 40, 94, 83)

# 2024/12/9
home_page_unfold_TO_yyl_page = (562, 617, 604, 660)

yyl_page_TO_shenshe_page = (884, 640, 919, 671)
yyl_page_TO_home_page_unfold = (41, 26, 74, 58)

shenshe_page_TO_dg_chose_page = (484, 209, 551, 286)
shenshe_page_TO_yyl_page = (50, 43, 75, 75)

dg_chose_page_TO_shenshe_page = (50, 43, 75, 75)  # 左上角的返回按钮

soul_content_page_TO_home_page_unfold = (28, 29, 62, 64)

home_page_unfold_TO_soul_content_page = (1119, 620, 1161, 662)

tp_main_TO_ltp_page = (1212, 365, 1255, 465)

ltp_page_TO_tp_main = (1218, 252, 1252, 327)

# 2024/12/10
ts_main_TO_ql_page = (1053, 641, 1093, 689)

ql_page_TO_ts_main = (40, 27, 69, 59)
# 2024/12/12
yyl_page_TO_ward_page = (1077, 632, 1124, 675)
ward_page_TO_yyl_page = (28, 26, 59, 63)

backstreet_page_TO_fm_page = (776, 111, 790, 191)

server_TO_home_page_fold = (592, 579, 687, 613)

# 识图点击的切换方式--------------------------------------------------------------------
# step_ts = ["task/based/switchui/res/step_ts.bmp", (293, 136, 1039, 231), "step_ts"]
# step_back_street = ["task/based/switchui/res/back_street.bmp", (206, 329, 1062, 446), "back_street"]

home_page_unfold_TO_backstreet_page = "step_back_street"
home_page_unfold_TO_ts_main = "step_ts"
# 庭院到探索
HOME_PAGEUNFOLD_TO_TS = {
    "HOME_PAGEUNFOLD_TO_TS1": step_ts,
    "HOME_PAGEUNFOLD_TO_TS2": step_ts_1,
    "HOME_PAGEUNFOLD_TO_TS3": step_ts_2,
    "HOME_PAGEUNFOLD_TO_TS4": step_ts_3,
}
# 庭院到町中
HOME_PAGEUNFOLD_TO_BACKSTREET = {
    "HOME_PAGEUNFOLD_TO_BACKSTREET1": step_back_street,
    "HOME_PAGEUNFOLD_TO_BACKSTREET2": step_back_street_1,
    "HOME_PAGEUNFOLD_TO_BACKSTREET3": step_back_street_2,
    "HOME_PAGEUNFOLD_TO_BACKSTREET4": step_back_street_3,
}

step_back = ["task/based/switchui/res/step_back.bmp", (11, 12, 183, 209), "step_back"]
step_back_2 = ["task/based/switchui/res/step_back_2.bmp", (11, 12, 183, 209), "step_back_2"]
step_back_3 = ["task/based/switchui/res/step_back_3.bmp", (11, 12, 183, 209), "step_back_3"]

# 两种返回的识图样式
BACK = {"BACK1": step_back, "BACK2": step_back_2, "BACK3": step_back_3}

step_soul_content_1 = ["task/based/switchui/res/step_soul_content_1.bmp", [1214, 615, 1250, 653], "step_soul_content_1"]
step_soul_content_2 = ["task/based/switchui/res/step_soul_content_2.bmp", [1034, 568, 1063, 603], "step_soul_content_2"]
step_soul_content_3 = ["task/based/switchui/res/step_soul_content_3.bmp", [1186, 501, 1239, 543], "step_soul_content_3"]

# 式神录
SOUL_CONTENT = {
    "SOUL_CONTENT1": step_soul_content_1,
    "SOUL_CONTENT2": step_soul_content_2,
    "SOUL_CONTENT3": step_soul_content_3,
}
# 识图点击部分
