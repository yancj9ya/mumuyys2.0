from PIGEON.MidTrans import Task
from PIGEON.log import Log
import sys
import os

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 将当前目录添加到 sys.path 中
if current_dir not in sys.path:
    sys.path.append(current_dir)
