from page.page_switch import nav
from tool.soulchange.soulchange import SoulChange
from tool.soulchange.res.img_info_auto_create import *
from tool.Mytool.imageRec import ImageRec
from tool.Mytool.windows import Windows
from tool.Mytool.Ocr import Ocr
from tool.Mytool.Click import Click
import time, win11toast


if __name__ == "__main__":
    from task.jysk.res.img_info_auto_create import *

    click = Click()
    for i in range(10):
        click.click(441, 329)
        click.mouse_scroll(["down", 6], 441, 329)
        print(i)
        time.sleep(1)
