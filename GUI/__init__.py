from GUI.main import App
from GUI.togglebuton import ToggleButton
import sys
import os

# 获取当前包所在的目录路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 将当前目录添加到 sys.path 中
if current_dir not in sys.path:
    sys.path.append(current_dir)
