# This file is used to capture the screenshot of the game window and send mouse events to the game window.
#
#

import win32gui
import win32ui
import win32con
import time
import numpy as np
import cv2
from ctypes import windll
from PIGEON.log import Log

log = Log()
# from Mytool.nemu.mumuScreencap import MuMuScreenCap

WM_LBUTTONDOWN = 0x0201
WM_SERCURSOR = 0x20
WM_MOUSEACTIVATE = 0x21
WM_MOUSEMOVE = 0x0200
WM_LBUTTONUP = 0x0202
WM_PARENTNOTIFY = 0x210
WM_MOUSEWHEEL = 0x020A

MK_LBUTTON = 0x0001
HTCLIENT = 1

PostMessage = windll.user32.PostMessageW
SendMessage = windll.user32.SendMessageW

FindWindow = win32gui.FindWindow
FindWindowEx = win32gui.FindWindowEx


class Windows:
    LOCK = False  # 主要是为了截图互斥，防止竞争设备上下文导致的错误
    # mumu_sc = MuMuScreenCap(
    #     0, "H:\MuMuPlayer-12.0-1", displayId=0
    # )  # mumu自身的ipc截图方式，创建链接木木模拟器的实例

    def __init__(self):
        # windows截图的方式,必须获取窗口句柄handle
        self.par_handle = self.get_handle("MuMu模拟器12")
        self.child_handle = self.get_handleEx(self.par_handle, "MuMuPlayer")

        pass

    @classmethod
    def get_handle(cls, title: str) -> int:
        return win32gui.FindWindow(None, title)

    @classmethod
    def get_handleEx(cls, par_handle: int, title: str) -> int:
        return win32gui.FindWindowEx(par_handle, None, None, title)

    @classmethod
    def screenshot(cls, hwnd: int, area: list, save_img=False, method="win_shot") -> np.ndarray:
        match method:
            case "win_shot":
                while cls.LOCK:  # locked
                    time.sleep(0.01)  # wait for release lock
                else:
                    cls.LOCK = True  # set lock

                    hwindc = None
                    srcdc = None
                    memdc = None
                    bmp = None
                    img = None

                    try:
                        # 计算截图区域
                        w, h = area[2] - area[0], area[3] - area[1]

                        # 获取窗口设备上下文
                        hwindc = win32gui.GetWindowDC(hwnd)
                        srcdc = win32ui.CreateDCFromHandle(hwindc)
                        memdc = srcdc.CreateCompatibleDC()
                        bmp = win32ui.CreateBitmap()
                        bmp.CreateCompatibleBitmap(srcdc, w, h)
                        memdc.SelectObject(bmp)

                        # 从源设备上下文复制位图到内存设备上下文
                        memdc.BitBlt((0, 0), (w, h), srcdc, (area[0], area[1]), win32con.SRCCOPY)

                        # 获取位图数据并转换为图像数组
                        signedIntsArray = bmp.GetBitmapBits(True)
                        img = np.frombuffer(signedIntsArray, dtype="uint8").reshape(h, w, 4)
                        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                    except Exception as e:
                        log.error(f"截图失败，错误信息: {e}")
                        return None

                    finally:
                        # 清理资源
                        if srcdc:
                            srcdc.DeleteDC()
                        if memdc:
                            memdc.DeleteDC()
                        if hwindc:
                            win32gui.ReleaseDC(hwnd, hwindc)
                        if bmp:
                            win32gui.DeleteObject(bmp.GetHandle())
                        if cls.LOCK:
                            cls.LOCK = False  # release lock
            case "nemu_ipc":
                try:
                    whole_img = cls.mumu_sc.screencap_raw()
                    img = whole_img[area[1] : area[3], area[0] : area[2]]
                except Exception as e:
                    log.error(f"截图失败，错误信息: {e}")
                    return None

        # 保存图像或返回处理后的图像
        if save_img:
            timestamp = time.strftime("(%Y-%m-%d)  %H时%M分", time.localtime())
            path = f"task/dg/awards/{timestamp}.jpg"
            cv2.imencode(".jpg", img)[1].tofile(path)
            log.info(f"截图成功，保存路径为:\n{path}")
            return None  # 如果保存图像，则返回 None

        return img

    def notifyparent(self, x, y):
        msg = WM_PARENTNOTIFY
        wparam = WM_LBUTTONDOWN
        Lparam = y << 16 | x
        SendMessage(self.par_handle, msg, wparam, Lparam)

    def mouse_move(self, x, y):
        msg = WM_MOUSEMOVE
        wparam = MK_LBUTTON
        Lparam = y << 16 | x
        PostMessage(self.child_handle, msg, wparam, Lparam)

    def mouseactivate(self):
        msg = WM_MOUSEACTIVATE
        wparam = self.par_handle
        Lparam = WM_LBUTTONDOWN << 16 | HTCLIENT
        SendMessage(self.child_handle, msg, wparam, Lparam)

    def setcursor(self):
        msg = WM_SERCURSOR
        wparam = self.child_handle
        Lparam = WM_LBUTTONDOWN << 16 | HTCLIENT
        SendMessage(self.child_handle, msg, wparam, Lparam)

    def left_down(self, x, y):
        msg = WM_LBUTTONDOWN
        wparam = MK_LBUTTON
        Lparam = y << 16 | x
        PostMessage(self.child_handle, msg, wparam, Lparam)

    def left_up(self, x, y):
        msg = WM_LBUTTONUP
        wparam = 0
        Lparam = y << 16 | x
        PostMessage(self.child_handle, msg, wparam, Lparam)

    def wheel_scroll(self, delta, x, y):
        msg = WM_MOUSEWHEEL
        wparam = delta << 16
        Lparam = y << 16 | x
        PostMessage(self.child_handle, msg, wparam, Lparam)

    def get_window_rect(self) -> list:
        return win32gui.GetWindowRect(self.child_handle)

    def x_button_down(self, x, y):
        msg = WM_XBUTTONDOWN
        wparam = MK_XBUTTON1
        Lparam = y << 16 | x
        PostMessage(self.child_handle, msg, wparam, Lparam)

    def x_button_up(self, x, y):
        msg = WM_XBUTTONUP
        wparam = MK_XBUTTON1
        Lparam = y << 16 | x
        PostMessage(self.child_handle, msg, wparam, Lparam)


if __name__ == "__main__":
    import sys

    sys.path.append("your_path_to_Mytool")

    w = Windows()
    print(f"窗口句柄:parent_handle={w.par_handle}, child_handle= {w.child_handle}\n")
    # 分身N1
    par_handle = w.get_handle("#N1 阴阳师 - MuMu模拟器12")
    child_handle = w.get_handleEx(par_handle, "MuMuPlayer")
    print(f"分身N1的窗口句柄: par={par_handle}, child={child_handle}")
