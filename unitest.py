from page.page_switch import nav
from tool.soulchange.soulchange import SoulChange
from tool.soulchange.res.img_info_auto_create import *
from tool.Mytool.imageRec import ImageRec
from tool.Mytool.windows import Windows
from tool.Mytool.Ocr import Ocr
from tool.Mytool.Click import Click
import time, win11toast


if __name__ == "__main__":
    ocr = Ocr()
    text_area = (665, 426, 715, 453)
    pattern = "([0-9]{3})"
    range_color = ["ab3810", (100, 60, 100)]

    for _ in range(5):
        # res = ocr.ocr_by_re((1155, 22, 1238, 52), r"\d+", range_color=["afaa9f", (10, 16, 131)], debug=True)
        # res = ocr.ocr_by_re(text_area, pattern, debug=True, threshold=0.7)
        # res = ocr.ocr_by_re((1065, 233, 1104, 256), r"\d+", range_color=["eac15d", (20, 100, 100)], debug=True)
        res = ocr.ocr_by_re(text_area, r"\d+", range_color=range_color, debug=True)
        if res:
            print(res.group(0))
