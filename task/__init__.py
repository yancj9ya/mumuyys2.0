from task.tp.tp import Tp
from task.dg.dg import Dg
from task.ltp.ltp import Ltp
from task.ql.ql import Ql
from task.hd.hd import Hd
from task.ts.ts import Ts
from task.yh.yh import Yh
from task.xz.xz import Xz


import sys
import os

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 将当前目录添加到 sys.path 中
if current_dir not in sys.path:
    sys.path.append(current_dir)
