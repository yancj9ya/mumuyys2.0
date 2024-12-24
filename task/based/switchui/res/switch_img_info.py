home_page_unfold = ["task/based/switchui/res/home_page_unfold.bmp", [493, 16, 524, 50], "home_page_unfold"]
home_page_fold = ["task/based/switchui/res/home_page_fold.bmp", [365, 37, 392, 76], "home_page_fold"]
tp_end_mark_ui = ["task/based/switchui/res/end_mark_ui.bmp", [177, 637, 196, 677], "tp_end_mark_ui"]
tp_main_damo = ["task/based/switchui/res/tp_main_damo.bmp", [560, 475, 662, 551], "tp_main_damo"]
tp_main_ui = ["task/based/switchui/res/tp_main_ui.bmp", [40, 446, 112, 497], "tp_main_ui"]
damo_ui = ["task/based/switchui/res/damo_ui.bmp", [562, 497, 685, 580], "damo_ui"]


ts_main_ui = ["task/based/switchui/res/ts_main_ui.bmp", [1133, 119, 1180, 172], "ts_main_ui"]
ts_tz_ui = ["task/based/switchui/res/ts_tz_ui.bmp", [879, 508, 1012, 570], "ts_tz_ui"]
ts_cm_ui = ["task/based/switchui/res/ts_cm_ui.bmp", [798, 645, 833, 686], "ts_cm_ui"]
ts_end_mark_ui = ["task/based/switchui/res/ts_end_mark_ui.bmp", [67, 649, 94, 672], "ts_end_mark_ui"]

# 2024/12/8 add
area_demon_ui = ["task/based/switchui/res/area_demon_ui.bmp", [49, 369, 84, 434], "area_demon_ui"]

# 2024/12/9 add
yyl_page = ["task/based/switchui/res/yyl_page.bmp", [879, 633, 922, 682], "yyl_page"]
shenshe_page = ["task/based/switchui/res/shenshe_page.bmp", [216, 216, 288, 286], "shenshe_page"]
dg_chose_page = ["task/based/switchui/res/dg_chose_page.bmp", [146, 613, 194, 661], "dg_chose_page"]
soul_content_page = ["task/based/switchui/res/soul_content_page.bmp", [133, 25, 162, 60], "soul_content_page"]
ltp_page = ["task/based/switchui/res/ltp_page.bmp", [69, 635, 117, 674], "ltp_page"]

# 2024/12/10 add
ql_page = ["task/based/switchui/res/ql_page.bmp", [107, 22, 173, 62], "ql_page"]
ward_page = ["task/based/switchui/res/ward_page.bmp", (183, 343, 371, 584), "ward_page"]


backstreet_page = ["task/based/switchui/res/backstreet_page.bmp", [769, 390, 791, 494], "backstreet_page"]
fm_page = ["task/based/switchui/res/fm_page.bmp", [12, 656, 54, 704], "fm_page"]
server_page = ["task/based/switchui/res/server_page.bmp", [20, 360, 400, 700], "server_page"]

# 识图点击的切换方式--------------------------------------------------------------------
step_ts = ["task/based/switchui/res/step_ts.bmp", (293, 136, 1039, 231), "step_ts"]
step_back_street = ["task/based/switchui/res/back_street.bmp", (206, 329, 1062, 446), "back_street"]


ui_list = locals()
ui_list_keys = list(ui_list.keys())[8:]


if __name__ == "__main__":
    print(ui_list_keys)
