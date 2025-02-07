from page.page_switch import nav
from tool.soulchange.soulchange import SoulChange
from tool.soulchange.res.img_info_auto_create import *
from tool.Mytool.imageRec import ImageRec

if __name__ == "__main__":
    # IMAGE_REC = ImageRec()

    # CHECKED = ["tool/soulchange/res/CHECKED.bmp", [1234, 167, 1252, 218], "CHECKED"]  # [1236, 100, 1253, 149]
    # UNCHECK = ["tool/soulchange/res/UNCHECK.bmp", [1234, 167, 1252, 218], "UNCHECK"]  # [1234, 167, 1252, 218]
    # GROUP_LIST = [GROUP1, GROUP2, GROUP3, GROUP4, GROUP5, GROUP6, GROUP7]

    # for group in GROUP_LIST:
    #     CHECKED[1] = group
    #     # print(CHECKED)
    #     res = IMAGE_REC.match_color_img_by_hist(CHECKED)  # CHECKED UNCHECK
    #     # print(CHECKED[2], res)
    #     print(f"{res}-{bool(res)}:{GROUP_LIST.index(group)}")

    souL_C = SoulChange()
    souL_C.confirm_plan("2")
