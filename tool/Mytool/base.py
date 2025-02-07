from ctypes import windll
from ctypes.wintypes import HWND
import cv2
import numpy as np
import win32con
import win32gui
import win32ui,win32com.client
import time
import ctypes
from ctypes import wintypes

class windowControl:
    def __init__(self):
        # 预处理区------------------------------------------------------------------
        self.PostMessageW = windll.user32.PostMessageW
        self.ClientToScreen = windll.user32.ClientToScreen
        # 鼠标
        self.WM_MOUSEMOVE = 0x0200
        self.WM_LBUTTONDOWN = 0x0201
        self.WM_LBUTTONUP = 0x202
        self.WM_MOUSEWHEEL = 0x020A
        self.WHEEL_DELTA = 120
        # 鼠标
        self.GetDC = windll.user32.GetDC
        self.CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
        self.GetClientRect = windll.user32.GetClientRect
        self.CreateCompatibleBitmap = windll.gdi32.CreateCompatibleBitmap
        self.SelectObject = windll.gdi32.SelectObject
        self.BitBlt = windll.gdi32.BitBlt
        self.SRCCOPY = 0x00CC0020
        self.GetBitmapBits = windll.gdi32.GetBitmapBits
        self.DeleteObject = windll.gdi32.DeleteObject
        self.ReleaseDC = windll.user32.ReleaseDC


        # 排除缩放干扰
        windll.user32.SetProcessDPIAware()

    def window_part_shot(self, hwnd, x1, y1, x2, y2, save_img=False):
        """
        窗口区域截图
        :param hwnd: 窗口句柄
        :param x1: 截图区域的左上角x坐标
        :param y1: 截图区域的左上角y坐标
        :param x2: 截图区域的右下角x坐标
        :param y2: 截图区域的右下角y坐标
        :param save_img: 是否保存图片
        """
        try:
            # 调整坐标以适应窗口边框
            y1, y2 = int(y1) + 31, int(y2) + 31
            x1, x2 = int(x1) + 8, int(x2) + 8
            w, h = x2 - x1, y2 - y1

            # 获取窗口设备上下文
            hwindc = win32gui.GetWindowDC(hwnd)
            srcdc = win32ui.CreateDCFromHandle(hwindc)
            memdc = srcdc.CreateCompatibleDC()
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(srcdc, w, h)
            memdc.SelectObject(bmp)

            # 从源设备上下文复制位图到内存设备上下文
            memdc.BitBlt((0, 0), (w, h), srcdc, (x1, y1), win32con.SRCCOPY)

            # 获取位图数据并转换为图像数组
            signedIntsArray = bmp.GetBitmapBits(True)
            img = np.frombuffer(signedIntsArray, dtype='uint8').reshape(h, w, 4)

            # 清理资源
            srcdc.DeleteDC()
            memdc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwindc)
            win32gui.DeleteObject(bmp.GetHandle())

            if save_img:
                timestamp = time.strftime("(%Y-%m-%d)  %H时%M分", time.localtime())
                path = f'img/dgimg/{timestamp}.jpg'
                cv2.imencode('.jpg', img)[1].tofile(path)
                print(f"截图成功，保存路径为{path}")
            else:
                return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        except Exception as e:
            print(f"Error in window_part_shot: {e}")
            return None

    def left_down(self, handle: HWND, x: int, y: int):
        """在坐标(x, y)按下鼠标左键

        Args:
            handle (HWND): 窗口句柄
            x (int): 横坐标
            y (int): 纵坐标
        """
        wparam = 0
        lparam = y << 16 | x
        self.PostMessageW(handle, self.WM_LBUTTONDOWN, wparam, lparam)

    def left_up(self, handle: HWND, x: int, y: int):
        """在坐标(x, y)放开鼠标左键

        Args:
            handle (HWND): 窗口句柄
            x (int): 横坐标
            y (int): 纵坐标
        """
        wparam = 0
        lparam = y << 16 | x
        self.PostMessageW(handle, self.WM_LBUTTONUP, wparam, lparam)
        
    def scroll_mouse(self, handle: HWND, x: int, y: int, delta: int):
        """在坐标(x, y)滚动鼠标

        Args:
            handle (HWND): 窗口句柄
            x (int): 横坐标
            y (int): 纵坐标
            delta (int): 滚动量，正值表示向上滚动，负值表示向下滚动
        """
        wparam = delta << 16
        lparam = y << 16 | x
        self.PostMessageW(handle, self.WM_MOUSEWHEEL, wparam, lparam)
        print(f"滚动鼠标，delta={delta}")

    '''
    def restore_window(self, hwnd):
        """
        将指定窗口从最小化状态恢复到原来的大小
        :param hwnd: 窗口句柄
        """
        try:
            # 恢复窗口到原来的大小
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        except Exception as e:
            print(f"Error in restore_window: {e}")
    @staticmethod
    def bring_to_top(hwnd):
        """
        将指定窗口移动到最顶层
        :param hwnd: 窗口句柄
        """
        try:
            
            # 将窗口移动到最顶层
            win32gui.SetForegroundWindow(hwnd)
        except Exception as e:
            print(f"Error in bring_to_top: {e}")'''


    @staticmethod
    def get_hwnd_by_name(window_name):
        """
        根据窗口名获取窗口句柄
        :param window_name: 窗口名
        :return: 窗口句柄
        """
        try:
            hwnd = win32gui.FindWindow(None, window_name)
            if hwnd:
                return hwnd
            else:
                #print(f"未找到窗口名称为 '{window_name}' 的窗口")
                return None
        except Exception as e:
            print(f"Error in get_hwnd_by_name: {e}")
            return None

    def set_window_size(self, hwnd, width, height):
        """
        设置窗口的大小
        :param hwnd: 窗口句柄
        :param width: 窗口宽度
        :param height: 窗口高度
        """
        try:
            # 获取窗口的当前位置和大小
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            # 计算新的窗口大小
            new_width = right - left
            new_height = bottom - top
            # 调整窗口大小
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, left, top, width, height, win32con.SWP_SHOWWINDOW)
            print(f"窗口大小已设置为 {width}x{height}")
        except Exception as e:
            print(f"Error in set_window_size: {e}")

    def close_window_by_handle(self):
        self.PostMessageW(self.handle, win32con.WM_CLOSE, 0, 0)
        



import subprocess

def kill_process_by_window_title(window_title):
    try:
        # 使用tasklist命令查找窗口标题对应的进程ID
        tasklist_output = subprocess.check_output(['tasklist', '/FI', f'WINDOWTITLE eq {window_title}']).decode('gbk')
        print(f"找到进程: {tasklist_output}")
        for line in tasklist_output.split('\n'):
            if 'onmyoji.exe' in line:
                parts = line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    # 使用taskkill命令杀死进程
                    subprocess.call(['taskkill', '/PID', pid, '/F'])
                    print(f"已杀死进程: {pid}")
                    return
    except subprocess.CalledProcessError as e:
        print(f"错误: {e}")


