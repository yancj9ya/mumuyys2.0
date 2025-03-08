from task.tp.tp import Tp
from task.dg.dg import Dg
from task.ltp.ltp import Ltp
from task.ql.ql import Ql
from task.hd.hd import Hd
from task.ts.ts import Ts
from task.yh.yh import Yh
from task.xz.xz import Xz
from task.jy.jy import Jy
from task.fm.fm import Fm
from task.sixgate.sixgate import SixGate
from task.shadowgate.shadowgate import ShadowGate
from task.hunt.hunt import Hunt
from task.shutdown.auto_power_off import AutoPowerOff
from task.frog.frog import Frog
from task.areademon.areademon import Ad
from task.jysk.jysk import Jysk
from task.superking.cgw import Cgw
import enum


class Task(enum.Enum):
    契灵 = Ql
    智能 = Hd
    绘卷 = Ts
    御魂 = Yh
    道馆 = Dg
    寮突破 = Ltp
    狩猎战 = Hunt
    逢魔之时 = Fm
    结界寄养 = Jy
    结界突破 = Tp
    地域鬼王 = Ad
    六道之门 = SixGate
    阴界之门 = ShadowGate
    自动关机 = AutoPowerOff
    对弈竞猜 = Frog
    结界上卡 = Jysk
    超鬼王 = Cgw


# import sys
# import os

# # 获取当前文件的目录
# current_dir = os.path.dirname(os.path.abspath(__file__))

# # 将当前目录添加到 sys.path 中
# if current_dir not in sys.path:
#     sys.path.append(current_dir)
