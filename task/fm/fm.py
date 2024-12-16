# 逢魔之魂
from task.based.Mytool.Click import Click
from task.based.Mytool.imageRec import ImageRec
from task.based.Mytool.Ocr import Ocr
from task.based.Mytool.Counter import Counter
from task.hd.res.img_info import *
from time import sleep, time, strftime, localtime
from datetime import datetime
from PIGEON.log import log
from random import choices, uniform


class Fm:
    def __init__(self, running=None):
        self.running = running
