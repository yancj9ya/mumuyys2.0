from page.page_switch import nav
from tool.soulchange.soulchange import SoulChange
from tool.soulchange.res.img_info_auto_create import *
from tool.Mytool.imageRec import ImageRec
from tool.Mytool.windows import Windows
import time

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

    wn = Windows()
    print(wn.par_handle)
    print(wn.handle)
    # wn.mouseactivateX()
    # wn.setcursorX()
    wn.x_button_down(735, 547)
    time.sleep(0.1)
    wn.x_button_up(735, 547)
