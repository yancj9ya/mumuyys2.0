from page.page_switch import nav
from tool.soulchange.soulchange import SoulChange
from tool.soulchange.res.img_info_auto_create import *
from tool.Mytool.imageRec import ImageRec
from tool.Mytool.windows import Windows
from tool.Mytool.Ocr import Ocr
from tool.wxocr.wxocr import WxOcr
from tool.Mytool.Click import Click
import time, win11toast
from PIGEON.event import MyEvent
from PIGEON.client import Client

if __name__ == "__main__":

    client = Client()
    res = client.get_game_status()
    print(res)
